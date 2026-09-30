# [M] M-1 Insufﬁcient role isolation

## Summary
Severity: Medium
Contest weight: 0.1054
Dataset id: 7961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract defines several privileged roles such as a default admin role, a platform manager role, an upgrader role and a KYC manager role. During deployment the address that creates the contract is granted all of these roles, and the default admin role is also allowed to execute any function on the contract, not only role‑granting operations. This conflates the technical administrator, who should only be able to assign and revoke permissions, with business‑level managers who control platform logic, upgrades and KYC processes. Because the same address holds both sets of privileges, an attacker who can socially engineer the deployer or compromise that address can invoke any privileged function – for example changing platform parameters, upgrading the contract to a malicious implementation, or altering KYC status – without needing separate authorisation. The impact is that unauthorized changes to contract state may occur, potentially leading to loss of funds, disruption of service, or erosion of trust in the protocol. The vulnerability manifests whenever the contract is deployed with the deployer holding multiple roles, and it persists as long as the role checks do not distinguish between technical admin and business manager permissions. It was discovered during a manual audit that examined role assignments and noticed that the default admin role was used as a catch‑all permission holder. The issue is subtle because the code compiles and the role checks appear to work; however, the overlapping privileges are not obvious from a surface review. To remediate, the default admin role should be limited to granting and revoking other roles only, and the deployer should not be granted any business‑level roles. Each business function should have its own dedicated role, and the grantRole calls that assign platform manager, upgrader or KYC manager privileges to the admin should be removed. Applying the principle of least privilege restores proper isolation between technical administration and business logic, reducing the attack surface for social‑engineering and insider threats.

## Recommendation
DEFAULTADMINROLE should be used to grant roles only and nothing else. The deployer may have this
role, but they should not be granted any other roles.
• FantiumNFTV1.sol#L121,
• FantiumNFTV1.sol#L130,
• FantiumMinterV1.sol#L61,
• FantiumMinterV1.sol#L71,
• FantiumMinterV1.sol#L211,
• FantiumMinterV1.sol#L221
It creates confusion between a role that is supposed to manage the technical side of the contract and the
role of the platform manager responsible for the business logic consistency. This creates difﬁculties in role
management and has the potential to introduce errors related to the functionality permitted to each role.
Thus, it is recommended to remove these lines in FantiumNFTV1.sol#L18:
grantRole(PLATFORMMANAGER_ROLE, msg.sender);
...
grantRole(UPGRADERROLE, msg.sender);
...
hasRole(DEFAULTADMINROLE, msg.sender),
...
hasRole(DEFAULTADMINROLE, msg.sender),
Also, remove the lines in FantiumMinterV1.sol#L96-L98:
hasRole(DEFAULTADMINROLE, msg.sender),
...
hasRole(DEFAULTADMINROLE, msg.sender),
...
grantRole(KYCMANAGER_ROLE, msg.sender);
grantRole(PLATFORMMANAGER_ROLE, msg.sender);
grantRole(UPGRADERROLE, msg.sender);
