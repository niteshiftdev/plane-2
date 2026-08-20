import os
import uuid

from plane.bgtasks.dummy_data_task import create_dummy_data
from plane.db.models import Profile, Project, User, Workspace, WorkspaceMember
from plane.license.models import Instance, InstanceAdmin

email = os.environ["SEED_EMAIL"]
password = os.environ["SEED_PASSWORD"]
slug = os.environ["SEED_WORKSPACE"]

user = User.objects.filter(email=email).first()
if user is None:
    user = User.objects.create(
        email=email,
        username=uuid.uuid4().hex,
        display_name="Dev User",
        first_name="Dev",
        last_name="User",
    )
user.set_password(password)
user.is_password_autoset = False
user.is_email_verified = True
user.save()

profile, _ = Profile.objects.get_or_create(user=user)
profile.is_onboarded = True
profile.is_tour_completed = True
profile.onboarding_step = {
    "profile_complete": True,
    "workspace_create": True,
    "workspace_invite": True,
    "workspace_join": True,
}

workspace = Workspace.objects.filter(slug=slug).first()
if workspace is None:
    workspace = Workspace.objects.create(slug=slug, name="Dev Workspace", owner=user)
WorkspaceMember.objects.get_or_create(workspace=workspace, member=user, defaults={"role": 20})
profile.last_workspace_id = workspace.id
profile.save()

# God mode accepts email and password sign-in after the instance is configured.
instance = Instance.objects.last()
if instance is not None:
    InstanceAdmin.objects.get_or_create(user=user, instance=instance, defaults={"role": 20})
    if not instance.is_setup_done:
        instance.is_setup_done = True
        instance.is_signup_screen_visited = True
        instance.save()

# A populated project lets previews open on representative application screens.
# module_count stays at least five because create_module_issues samples five.
if not Project.objects.filter(workspace=workspace).exists():
    create_dummy_data(
        slug=slug,
        email=email,
        members=[],
        issue_count=40,
        cycle_count=4,
        module_count=6,
        pages_count=6,
        intake_issue_count=5,
    )

print(f"seeded {email} in {slug} ({Project.objects.filter(workspace=workspace).count()} project(s))")
