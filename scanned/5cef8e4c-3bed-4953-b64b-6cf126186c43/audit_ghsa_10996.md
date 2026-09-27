# [M] EC-CUBE has a Vulnerability that Allows MFA Bypass in the Administrative Interface

## Summary
Severity: Medium
Advisory: GHSA-7rhv-h82h-vpjh
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-7rhv-h82h-vpjh
Type: github-advisory

## Affected
- Packagist: `ec-cube/ec-cube` — affected >=4.1.0

## Details
# Vulnerability Allowing MFA Bypass

## Affected EC-CUBE Versions
Versions: 4.1.0 – 4.3.1

## Vulnerability Overview
If an administrator’s ID and password are compromised, an issue exists that allows an attacker to bypass the normally required two-factor authentication (2FA) and log in to the administrative interface.

## Severity and Impact

**CVSS v3.1 score**  
Base score: 6.2 / Temporal score: 5.7 / Environmental score (after mitigation and countermeasures): 0.0

An attacker can forcibly overwrite the 2FA configuration of an account with administrative privileges. As a result, the legitimate administrator can be locked out, while the attacker can log in to the administrative interface and perform unauthorized actions such as viewing sensitive information or tampering with the website.

## Root Cause Details

There are flaws in the access control implementation for the 2FA settings page (`/admin/two_factor_auth/set`).

1. **TwoFactorAuthListener.php**  
   The route for the 2FA settings page (`admin_two_factor_auth_set`) is included in the list of routes excluded from the 2FA authentication check.

2. **TwoFactorAuthController.php**  
   Even for users who already have 2FA configured, the implementation allows reconfiguration (overwriting) of the 2FA secret key without passing 2FA authentication.

## Attack Preconditions and Steps

**Preconditions:**
- The attacker knows the administrative user’s ID and password.
- 2FA is enabled for that user.

**Attack Steps:**
1. Attempt to log in using the ID and password.
2. When the 2FA code entry screen is displayed, do not enter a code; instead, directly modify the URL to access `/admin/two_factor_auth/set`.
3. Because access is not denied, the attacker can generate and save (overwrite) a new 2FA secret key.


# MFAバイパスが可能な脆弱性

## EC-CUBEバージョン
バージョン:  4.1.0 ~ 4.3.1

## 脆弱性の概要
管理者のIDとパスワードが漏洩している場合、本来必要な2段階認証を回避して管理画面にログインできてしまう問題です。

## 深刻度と影響

CVSS3.1スコア：基本評価:6.2  / 現状評価:5.7  / 環境評価(緩和・対策後):0.0 

攻撃者は管理者権限を持つアカウントの2FA設定を強制的に上書きできます。これにより、正規の管理者を締め出しつつ、攻撃者自身が管理画面へログインし、機密情報の閲覧やWebサイトの改ざんなどの不正操作を行うことが可能になります。

## 脆弱性の詳細な原因

システムの実装において、2FA設定画面(/admin/two_factor_auth/set)へのアクセス制御に不備があり。

1. TwoFactorAuthListener.php
2FA認証チェックを除外するルート設定に、設定画面(admin_two_factor_auth_set)が含まれている。
2. TwoFactorAuthController.php
既に2FA設定済みのユーザーであっても、2FA認証を通過せずに新しい鍵の再設定(上書き)を受け入れてしまう仕様になっている。

## 攻撃の成立条件と手順

前提条件:
管理ユーザーのIDとパスワードを知っていること。
そのユーザーで2FAが有効化されていること。

攻撃手順:

1. IDとパスワードでログインを試行する。
2. 2FAコード入力画面が表示されるが、入力を行わずに直接URLを書き換えて /admin/two_factor_auth/set へアクセスする。
3. アクセスが拒否されないため、攻撃者は新しい2FA秘密鍵を発行し、保存(上書き)する。
4. 以降、攻撃者が作成した新しい2FAコードを使ってログインが可能になる。

## References
- https://github.com/EC-CUBE/ec-cube/security/advisories/GHSA-7rhv-h82h-vpjh
- https://github.com/EC-CUBE/ec-cube/commit/094785943bfc3815c29f0cce9dbabb9bcc688474
- https://github.com/EC-CUBE/ec-cube
