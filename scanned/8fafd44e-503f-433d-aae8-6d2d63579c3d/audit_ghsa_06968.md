# [M] Kimai has Improper Authorization in Team Member and Team Activity Assignment APIs Which Allows Expansion of Team Scope Beyond Authorized Visibility

## Summary
Severity: Medium
Advisory: GHSA-xv4r-4885-gwpg
CVE: CVE-2026-52825
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-xv4r-4885-gwpg
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.58.0

## Details
### Summary

Kimai contains an authenticated improper authorization vulnerability in Team-related assignment APIs. A Teamlead who can edit their own team can use backend API endpoints to add users or activities that fall outside their intended visible or manageable scope, even when the frontend correctly hides those targets.

This affects both team member assignment and team activity assignment. The issue is caused by treating "may edit this team" as equivalent to "may attach any referenced object to this team", without performing a second authorization check on the target user or activity.

### Details

The issue affects at least the following API routes:

- `POST /api/teams/{id}/members/{userId}`
- `POST /api/teams/{id}/activities/{activityId}`

In both cases, the backend checks whether the caller may edit the `Team`, but it does not verify whether the referenced `User` or `Activity` falls inside the caller's allowed management scope.

For team member assignment, the frontend form correctly limits the visible user choices. In `src/Form/TeamEditForm.php`, the team edit form uses `UserType`:

```php
$builder->add('users', UserType::class, [
    'label' => 'add_user.label',
    'help' => 'team.add_user.help',
    'mapped' => false,
    'multiple' => false,
    'expanded' => false,
    'required' => false,
    'ignore_users' => $team !== null ? $team->getUsers() : []
]);
```

In `src/Form/Type/UserType.php`, the user selector is built from `UserRepository::getQueryBuilderForFormType()`:

```php
$query = new UserFormTypeQuery();
$query->setUser($options['user']);

$qb = $this->userRepository->getQueryBuilderForFormType($query);
$users = $qb->getQuery()->getResult();
```

And in `src/Repository/UserRepository.php`, Teamlead-visible candidates are limited to team members from teams they lead:

```php
if (null !== $user && $user->isTeamlead()) {
    $userIds = [];
    foreach ($user->getTeams() as $team) {
        if ($team->isTeamlead($user)) {
            foreach ($team->getUsers() as $teamMember) {
                $userIds[] = $teamMember->getId();
            }
        }
    }
    $userIds = array_unique($userIds);
    $qb->setParameter('teamMember', $userIds);
    $or->add($qb->expr()->in('u.id', ':teamMember'));
}
```

However, the actual member-assignment API does not reuse that restriction. In `src/API/TeamController.php`:

```php
#[IsGranted('edit', 'team')]
#[Route(methods: ['POST'], path: '/{id}/members/{userId}', name: 'post_team_member', requirements: ['id' => '\d+', 'userId' => '\d+'])]
public function postMemberAction(Team $team, #[MapEntity(mapping: ['userId' => 'id'])] User $member): Response
{
    if ($member->isInTeam($team)) {
        throw new BadRequestHttpException('User is already member of the team');
    }

    $team->addUser($member);
    $this->teamService->saveTeam($team);
}
```

For activity assignment, the same pattern appears. In `src/API/TeamController.php`:

```php
#[IsGranted('edit', 'team')]
#[Route(methods: ['POST'], path: '/{id}/activities/{activityId}', name: 'post_team_activity', requirements: ['id' => '\d+', 'activityId' => '\d+'])]
public function postActivityAction(Team $team, #[MapEntity(mapping: ['activityId' => 'id'])] Activity $activity, ActivityRepository $activityRepository): Response
{
    if ($team->hasActivity($activity)) {
        throw new BadRequestHttpException('Team has already access to activity');
    }

    $team->addActivity($activity);
    $activityRepository->saveActivity($activity);
}
```

The `Team` voter only checks whether the current user may edit that team, not whether the referenced object is within the Teamlead's legitimate scope. In `src/Voter/TeamVoter.php`:

```php
if (!$user->isAdmin() && !$user->isSuperAdmin() && !$user->isTeamleadOf($subject)) {
    return false;
}

return $this->permissionManager->hasRolePermission($user, $attribute . '_team');
```

For activities, this is especially risky because later authorization logic may trust the team assignment that was just written. In `src/Security/RolePermissionManager.php`:

```php
public function checkTeamAccessActivity(Activity $activity, User $user): bool
{
    if ($activity->getProject() !== null && !$this->checkTeamAccessProject($activity->getProject(), $user)) {
        return false;
    }

    return $this->checkTeamAccess($activity->getTeams(), $user);
}
```

So once a Teamlead is able to write a new team/activity relation, later access-control decisions may treat that relation as legitimate input.

*A PoC was provided, but removed for security reasons.*

### Impact

This vulnerability allows a Teamlead to use their own editable team as an expansion container for objects that should remain outside their authorized scope. In the validated member-assignment case, the attacker can forcibly add users who are not supposed to be manageable through that Teamlead's visible range. In the activity-assignment case, the attacker can attach activities that are outside the intended authorization boundary of the team.

Once such relations are written, downstream authorization, visibility, and business workflows may start treating them as legitimate. This can affect user scoping, team-based access control, customer/project/activity visibility, time-entry behavior, statistics, and reporting. The issue therefore breaks the trustworthiness of `Team` as a security isolation container.

# Solution

Several new permission checks were added to `src/API/TeamController.php` -
- Check if user can be accessed with `#[IsGranted('access_user', 'member')]` before adding as new team member 
- Check if customer can be seen with `#[IsGranted('view', 'customer')]` before a team is granted access to a customer
- Check if project can be seen with `#[IsGranted('view', 'project')]` before a team is granted access to a project
- Check if activity can be seen with `#[IsGranted('view', 'activity')]` before a team is granted access to an activity

See [https://www.kimai.org/en/security/ghsa-xv4r-4885-gwpg](https://www.kimai.org/en/security/ghsa-xv4r-4885-gwpg) for more information.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-xv4r-4885-gwpg
- https://github.com/kimai/kimai
