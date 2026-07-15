The code path is concrete and traceable. Let me verify the exact lines before rendering a verdict.

### Title
Empty-Keyring Passphrase Bypass Poisons Cached Passphrase, Causing First Key to Be Encrypted Under Attacker-Controlled Value — (`chia/util/file_keyring.py`)

---

### Summary

`FileKeyringContent.get_decrypted_data_dict` short-circuits to `return {}` with no cryptographic work when `self.data is None`. `FileKeyring.check_passphrase` treats the absence of an exception as proof of a valid passphrase, so it returns `True` for **any** string when the keyring file is in its initial empty state. The daemon's `unlock_keyring` RPC handler trusts this result and calls `Keychain.set_cached_master_passphrase(attacker_string)`. When the legitimate user subsequently adds their first key, `write_keyring` reads the cached passphrase and encrypts the key material under the attacker-controlled value.

---

### Finding Description

**Root cause — `FileKeyringContent.get_decrypted_data_dict`** [1](#0-0) 

`empty()` returns `True` whenever `self.data is None or len(self.data) == 0`. [2](#0-1) 

A freshly created `keyring.yaml` always has `data: null`, so `empty()` is `True` and the function returns `{}` before touching `symmetric_key_from_passphrase`, `decrypt_data`, or `CHECKBYTES_VALUE`. No cryptographic verification occurs.

**Propagation — `FileKeyring.check_passphrase`** [3](#0-2) 

The only signal `check_passphrase` uses is whether `get_decrypted_data_dict` raises. Because the empty-keyring path never raises, `check_passphrase` returns `True` for every string.

**Daemon RPC entry point — `unlock_keyring`** [4](#0-3) 

`Keychain.master_passphrase_is_valid(key, force_reload=True)` delegates through `KeyringWrapper.master_passphrase_is_valid` → `FileKeyring.check_passphrase`. [5](#0-4) 

When the check returns `True`, `Keychain.set_cached_master_passphrase(key)` stores the attacker's string as the in-process cached passphrase.

**First-write passphrase selection — `write_keyring`** [6](#0-5) 

When the keyring is still empty (`not self.has_content()`) and a cached passphrase exists, `write_keyring` unconditionally uses the cached value — no re-validation — to call `update_encrypted_data_dict`, which derives the symmetric key and encrypts the payload. [7](#0-6) 

The first key the user adds is therefore encrypted under the attacker-chosen passphrase.

---

### Impact Explanation

An attacker who can reach the daemon WebSocket (local process running as the same OS user, or any process with read access to the Chia SSL certificates in `~/.chia/mainnet/config/ssl/`) can:

1. Call `unlock_keyring {"key": "attacker_passphrase"}` before any keys are stored.
2. The daemon caches `"attacker_passphrase"` as the validated master passphrase.
3. When the legitimate user adds their first private key, `write_keyring` encrypts it under `"attacker_passphrase"`.
4. The attacker reads `keyring.yaml` (world-readable path, or readable by same user) and decrypts it with the known passphrase, recovering the BLS12-381 private key.
5. Full control over all XCH, CATs, NFTs, and any other assets controlled by that key.

This satisfies the **High** criterion: *bypass of daemon/keychain authorization that enables unauthorized key use*.

---

### Likelihood Explanation

The precondition (empty keyring) is the **default state** on every fresh Chia installation and after `chia keys delete_all`. The timing window is the entire period between daemon start and the moment the user first adds a key — potentially hours or days. Any malware or co-resident process running as the same OS user can exploit this without any brute-force or cryptographic attack.

---

### Recommendation

`get_decrypted_data_dict` must not bypass cryptographic verification for an empty keyring. `check_passphrase` should return `False` (or raise) when `self.data is None`, because there is no stored ciphertext to verify against. A correct guard:

```python
def check_passphrase(self, passphrase: str, force_reload: bool = False) -> bool:
    if force_reload:
        self.cached_file_content = FileKeyringContent.create_from_path(self.keyring_path)
    if self.cached_file_content.empty():
        return False   # No ciphertext → cannot validate any passphrase
    try:
        self.cached_file_content.get_decrypted_data_dict(passphrase)
        return True
    except Exception:
        return False
```

Separately, `unlock_keyring` should refuse to set the cached passphrase when the keyring has no content, since there is nothing to unlock.

---

### Proof of Concept

```python
# Reproducer (no daemon needed — pure unit test)
from chia._tests.util.keyring import TempKeyring
from chia.util.keyring_wrapper import KeyringWrapper

with TempKeyring() as temp_keyring:
    # Precondition: fresh empty keyring (data=None)
    assert not KeyringWrapper.get_shared_instance().has_master_passphrase()

    # Bug: any passphrase validates
    result = KeyringWrapper.get_shared_instance().master_passphrase_is_valid("wrong_passphrase")
    assert result is True   # FAILS the expected False — confirms the bug

    # Attacker poisons the cache (mirrors what unlock_keyring RPC does)
    from chia.util.keychain import Keychain
    Keychain.set_cached_master_passphrase("attacker_passphrase")

    # Victim adds first key — write_keyring uses cached passphrase
    keychain = Keychain()
    keychain.add_key("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about")

    # Attacker decrypts with known passphrase
    from chia.util.file_keyring import FileKeyringContent
    content = FileKeyringContent.create_from_path(
        KeyringWrapper.get_shared_instance().keyring.keyring_path
    )
    decrypted = content.get_decrypted_data_dict("attacker_passphrase")
    assert len(decrypted["keys"]) > 0   # Private key material recovered
```

### Citations

**File:** chia/util/file_keyring.py (L137-143)
```python
    def get_decrypted_data_dict(self, passphrase: str) -> dict[str, Any]:
        if self.empty():
            return {}
        key = symmetric_key_from_passphrase(passphrase, self.salt)
        encrypted_data_yml = base64.b64decode(yaml.safe_load(self.data or ""))
        data_yml = decrypt_data(encrypted_data_yml, key, self.nonce)
        return dict(yaml.safe_load(data_yml))
```

**File:** chia/util/file_keyring.py (L145-153)
```python
    def update_encrypted_data_dict(
        self, passphrase: str, decrypted_dict: DecryptedKeyringData, update_salt: bool
    ) -> None:
        self.nonce = generate_nonce()
        if update_salt:
            self.salt = generate_salt()
        data_yaml = yaml.safe_dump(decrypted_dict.to_dict())
        key = symmetric_key_from_passphrase(passphrase, self.salt)
        self.data = base64.b64encode(encrypt_data(data_yaml.encode(), key, self.nonce)).decode("utf-8")
```

**File:** chia/util/file_keyring.py (L155-156)
```python
    def empty(self) -> bool:
        return self.data is None or len(self.data) == 0
```

**File:** chia/util/file_keyring.py (L394-406)
```python
    def check_passphrase(self, passphrase: str, force_reload: bool = False) -> bool:
        """
        Attempts to validate the passphrase by decrypting keyring.data
        contents and checking the checkbytes value
        """
        if force_reload:
            self.cached_file_content = FileKeyringContent.create_from_path(self.keyring_path)

        try:
            self.cached_file_content.get_decrypted_data_dict(passphrase)
            return True
        except Exception:
            return False
```

**File:** chia/util/file_keyring.py (L436-439)
```python
        if not self.has_content() and KeyringWrapper.get_shared_instance().has_cached_master_passphrase():
            # TODO: The above checks, at the time of writing, make sure we get a str here.  A reconsideration of this
            #       interface would be good.
            passphrase = cast(str, KeyringWrapper.get_shared_instance().get_cached_master_passphrase()[0])
```

**File:** chia/daemon/server.py (L526-529)
```python
        try:
            if Keychain.master_passphrase_is_valid(key, force_reload=True):
                Keychain.set_cached_master_passphrase(key)
                success = True
```

**File:** chia/util/keyring_wrapper.py (L232-233)
```python
    def master_passphrase_is_valid(self, passphrase: str, force_reload: bool = False) -> bool:
        return self.keyring.check_passphrase(passphrase, force_reload=force_reload)
```
