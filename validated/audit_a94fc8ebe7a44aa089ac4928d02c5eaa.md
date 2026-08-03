[1](#0-0)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/datastructures/ordered_map.move (L129-138)
```text
    /// Remove a key/value pair from the map.
    /// Aborts with EKEY_NOT_FOUND if `key` doesn't exist.
    public fun remove<K: drop, V>(self: &mut OrderedMap<K, V>, key: &K): V {
        let len = self.entries.length();
        let index = binary_search(key, &self.entries, 0, len);
        assert!(index < len, error::invalid_argument(EKEY_NOT_FOUND));
        let Entry { key: old_key, value } = self.entries.remove(index);
        assert!(key == &old_key, error::invalid_argument(EKEY_NOT_FOUND));
        value
    }
```
