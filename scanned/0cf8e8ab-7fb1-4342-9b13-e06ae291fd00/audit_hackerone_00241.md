# [M] Allow authenticated users can edit, trash,and add new in BuddyPress Emails function

## Summary
Severity: Medium
Program: WordPress
Weakness: Privilege Escalation
Reporter: hoangkien1020
State: resolved
Disclosed: 2020-05-22T00:33:04.676Z
Source: https://hackerone.com/reports/833782

## Details
## Description:

Allow author can edit, trash,and add new your posts in BuddyPress Emails function
And editor can edit,trash, add new any posts in BuddyPress Emails default.
## Steps To Reproduce:

Step 1 : Create two accounts: Admin and Author
Step 2: Login with admin account. In admin account, give author to admin account.
Step 4: Login with author within dashboard
Access link:
*domain/wp-admin/edit.php?post_type=bp-email*
Step 5: Revoke author to author privilege in admin account
Step 6: Within author dashboard, author can edit, trash,and add new
PoC by video:
https://bit.ly/2UH7iLz
## Recommendations
Valid user current session access.

## Impact

Author can edit, trash,and add new in BuddyPress Emails.
And editor can edit,trash, add new any posts in BuddyPress Emails default.
