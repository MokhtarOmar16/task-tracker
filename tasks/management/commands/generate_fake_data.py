from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskCompletion, FriendRequest
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()
fake = Faker()


def make_aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


class Command(BaseCommand):
    help = "Generate fake data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=10, help="Number of users to create"
        )
        parser.add_argument(
            "--tasks", type=int, default=50, help="Number of tasks to create"
        )

    def handle(self, *args, **options):
        num_users = options["users"]
        num_tasks = options["tasks"]

        created_users = []
        for i in range(num_users):
            username = fake.unique.user_name()[:30]
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password="testpass123",
                full_name=fake.name(),
                bio=fake.text(max_nb_chars=200),
                task_goal=random.randint(3, 15),
                current_streak=random.randint(0, 30),
                longest_streak=random.randint(0, 50),
            )
            created_users.append(user)

        self.stdout.write(f"Created {num_users} users")

        users = list(User.objects.all())
        tasks_created = 0
        for _ in range(num_tasks):
            user = random.choice(users)
            created = make_aware(
                fake.date_time_between(start_date="-1y", end_date="now")
            )
            task = Task.objects.create(
                user=user,
                title=fake.sentence(nb_words=4),
                notes=fake.text() if random.random() > 0.3 else "",
                is_public=random.random() > 0.7,
                created_at=created,
            )
            tasks_created += 1

            if random.random() > 0.5:
                completed_at = created + timedelta(hours=random.randint(1, 72))
                task.completed_at = completed_at
                task.save()
                TaskCompletion.objects.create(task=task, completed_at=completed_at)

        self.stdout.write(f"Created {tasks_created} tasks")

        for _ in range(min(num_users * 2, 30)):
            from_user, to_user = random.sample(users, 2)
            if not FriendRequest.objects.filter(
                from_user=from_user, to_user=to_user
            ).exists():
                status = random.choice(["pending", "accepted", "declined"])
                fr = FriendRequest.objects.create(
                    from_user=from_user,
                    to_user=to_user,
                    status=status,
                )
                if status == "accepted":
                    fr.created_at = make_aware(
                        fake.date_time_between(start_date="-1y", end_date="now")
                    )
                    fr.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully generated fake data!"))
        self.stdout.write(f"Login with any username and password: testpass123")
