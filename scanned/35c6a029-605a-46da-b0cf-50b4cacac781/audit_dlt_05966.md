# [?] Added SharedMutex lock to sync.h, plus fixed deadlock detector 

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-11-27
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/fdfe72acc49ca722315db72bc637e079eaef7379
Type: security-commit

## Details
Added SharedMutex lock to sync.h, plus fixed deadlock detector 

Co-authored-by: Griffith probablyaplebeian@protonmail.com

Summary
-------

While investigating other issues, I noticed that our thread safety system
is missing any notion of a shared mutex (read-write lock).
As such, I went ahead and added it to our thread safety/annotations system.

Motivation:
We may need this in the future. Shared mutexes are very useful and
it pays to have them incorporated into our thread-safety system.
I also went ahead and backported from ABC the core backport that adds the
REVERSE_LOCK macro. This is ABC D6532 I also noticed that our thread safety
stuff that runs in debug mode is quite handy for detecting deadlocks, but
the error message it prints is slightly incorrect (it confuses
"previous lock order" with "current lock order").

I created an issue for this: #316. This closes #316.

Additionally, as described in issue #323, our deadlock detection code is
unable to detect cycles of the form:

Thread 1: Locks A, B
Thread 2: Locks B, C
Thread 3: Locks C, A

The above situation has been addressed in this MR, thus this closes #323.

This MR has the following changes:

- Backport of ABC D6532 (adding the REVERSE_LOCK macro).
- Fix the error message when potential_deadlock_detected fires
  (requires Debug build). The error message reversed previous and
  current lock order. Closes #316.
- Detect deadlock cycles involving more than 2 threads. Closes #323.
- Add the SharedMutex type (which is a wrapper around
  std::shared_mutex but contains thread-safety annotations similar to
  our Mutex and RecursiveMutex types).

  - You can lock this with LOCK() for exclusive access or
    the new LOCK_SHARED() for read-only access.
  - Also added the macros: WAIT_LOCK_SHARED() and TRY_LOCK_SHARED() which
    are similar to the existing macros, but lock in shared mode (read-only mode).
  - Thread safety annotations such as GUARDED_BY() "just work" with this
    new type now.
- Added unit test for SharedMutex to sync_tests.cpp
- Added a new exception to sync.h called PotentialDeadlockError
  which is only used by unit tests (if compiled in debug mode).
- Fixed the existing unit test in sync_tests.cpp to detect that the
  potential deadlock code is detecting the erroneous order .. in the
  proper order! (Tests that there will be no regressions for issue #316).
- Cleaned up the code a little bit in synch.h.
- Greg Griffith's BU deadlock tests were ported over. Thank you @ggriffith!
- Added a testing setup that can enable deadlock exceptions for a test fixture
  (rather than abort the app), named BasicTestingSetupWithDeadlockExceptions

Test Plan
---------

1. Compile with debug mode e.g. add -DCMAKE_BUILD_TYPE=Debug to the cmake line:
   `cmake -GNinja -DCMAKE_BUILD_TYPE=Debug ..`

   - `ninja all check` or you can simply do `ninja test_bitcoin` and
     `src/test/test_bitcoin -t sync_tests` and
     `src/test/test_bitcoin -t deadlock_tests`

   - Extra credit: Also run `ninja check-functional-extended`

2. Do the above again but do it with release mode:
   `-DCMAKE_BUILD_TYPE=Release`

### src/sync.cpp
```diff
@@ -10,8 +10,11 @@
 #include <util/threadnames.h>
 
 #include <cstdio>
+#include <functional>
 #include <map>
 #include <set>
+#include <system_error>
+#include <vector>
 
 #ifdef DEBUG_LOCKCONTENTION
 void PrintLockContention(const char *pszName, const char *pszFile, int nLine) {
@@ -39,26 +42,34 @@ struct CLockLocation {
         const char* pszFile,
         int nLine,
         bool fTryIn,
-        const std::string& thread_name)
+        const std::string& thread_name,
+        bool fRecursiveIn)
         : fTry(fTryIn),
           mutexName(pszName),
           sourceFile(pszFile),
           m_thread_name(thread_name),
-          sourceLine(nLine) {}
+          sourceLine(nLine),
+          fRecursive(fRecursiveIn) {}
 
     std::string ToString() const
     {
         return tfm::format(
-            "%s %s:%s%s (in thread %s)",
-            mutexName, sourceFile, itostr(sourceLine), (fTry ? " (TRY)" : ""), m_thread_name);
+            "%s %s:%s%s%s (in thread %s)",
+            mutexName, sourceFile, itostr(sourceLine), (fTry ? " (TRY)" : ""), (fRecursive ? " (RECURSIVE)": ""),
+            m_thread_name);
     }
 
+    const std::string & Name() const { return mutexName; }
+
+    bool IsRecursive() const { return fRecursive; }
+
 private:
     bool fTry;
     std::string mutexName;
     std::string sourceFile;
-    const std::string& m_thread_name;
+    const std::string m_thread_name;
     int sourceLine;
+    bool fRecursive;
 };
 
 typedef std::vector<std::pair<void *, CLockLocation>> LockStack;
@@ -77,7 +88,19 @@ struct LockData {
     LockOrders lockorders;
     InvLockOrders invlockorders;
     std::mutex dd_mutex;
+
+    /// For cycle detection: given a lock, the set of locks that were ever locked before it
+    std::set<void *> getParentsOf(void *cs) const;
 };
+
+std::set<void *> LockData::getParentsOf(void *cs) const {
+    std::set<void *> ret;
+    for (auto it = invlockorders.lower_bound({cs, nullptr}); it != invlockorders.end() && it->first == cs; ++it) {
+        ret.emplace_hint(ret.end(), it->second);
+    }
+    return ret;
+}
+
 LockData &GetLockData() {
     static LockData lockdata;
     return lockdata;
@@ -88,24 +111,30 @@ static thread_local LockStack g_lockstack;
 static void
 potential_deadlock_detected(const std::pair<void *, void *> &mismatch,
                             const LockStack &s1, const LockStack &s2) {
+    std::vector<void *> ids;
+    if (!g_debug_lockorder_abort) ids.reserve(4);
     LogPrintf("POTENTIAL DEADLOCK DETECTED\n");
     LogPrintf("Previous lock order was:\n");
     for (const std::pair<void *, CLockLocation> &i : s2) {
         if (i.first == mismatch.first) {
             LogPrintfToBeContinued(" (1)");
+            if (!g_debug_lockorder_abort) ids.emplace_back(i.first);
         }
         if (i.first == mismatch.second) {
             LogPrintfToBeContinued(" (2)");
+            if (!g_debug_lockorder_abort) ids.emplace_back(i.first);
         }
         LogPrintf(" %s\n", i.second.ToString());
     }
     LogPrintf("Current lock order is:\n");
     for (const std::pair<void *, CLockLocation> &i : s1) {
         if (i.first == mismatch.first) {
             LogPrintfToBeContinued(" (1)");
+            if (!g_debug_lockorder_abort) ids.emplace_back(i.first);
         }
         if (i.first == mismatch.second) {
             LogPrintfToBeContinued(" (2)");
+            if (!g_debug_lockorder_abort) ids.emplace_back(i.first);
         }
         LogPrintf(" %s\n", i.second.ToString());
     }
@@ -116,7 +145,37 @@ potential_deadlock_detected(const std::pair<void *, void *> &mismatch,
                 __FILE__, __LINE__);
         abort();
     }
-    throw std::logic_error("potential deadlock detected");
+    throw PotentialDeadlockError("potential deadlock detected",
+                                 {ids.size() > 0 ? ids[0] : nullptr, ids.size() > 1 ? ids[1] : nullptr},
+                                 {ids.size() > 2 ? ids[2] : nullptr, ids.size() > 3 ? ids[3] : nullptr});
+}
+
+static void
+potential_self_deadlock_detected(const CLockLocation &cur, const CLockLocation &prev, void *pcur) {
+    LogPrintf("POTENTIAL SELF-DEADLOCK DETECTED\n");
+    LogPrintf("Current locking location: %s, previous lock location: %s\n", cur.ToString(), prev.ToString());
+    if (g_debug_lockorder_abort) {
+        fprintf(stderr,
+                "Assertion failed: detected thread that deadlocks itself at %s:%i [%s], "
+                "details in debug log.\n",
+                __FILE__, __LINE__, cur.ToString().c_str());
+        abort();
+    }
+    throw PotentialDeadlockError("potential deadlock detected", {pcur, pcur}, {pcur, pcur});
+}
+
+static void
+potential_deadlock_cycle_detected(const CLockLocation &cur, void *l1, void *l2, void *cs) {
+    LogPrintf("POTENTIAL DEADLOCK CYCLE DETECTED\n");
+    LogPrintf("Current locking location: %s\n", cur.ToString());
+    if (g_debug_lockorder_abort) {
+        fprintf(stderr,
+                "Assertion failed: detected a potentially deadlicking lock cycle at %s:%i [%s], "
+                "details in debug log.\n",
+                __FILE__, __LINE__, cur.ToString().c_str());
+        abort();
+    }
+    throw PotentialDeadlockError("potential deadlock detected", {l1, l2}, {cs, l1});
 }
 
 static void push_lock(void *c, const CLockLocation &locklocation) {
@@ -125,33 +184,78 @@ static void push_lock(void *c, const CLockLocation &locklocation) {
 
     g_lockstack.push_back(std::make_pair(c, locklocation));
 
+    size_t iterCt = 0;
     for (const std::pair<void *, CLockLocation> &i : g_lockstack) {
+        ++iterCt;
         if (i.first == c) {
-            break;
+            if (iterCt == g_lockstack.size() || locklocation.IsRecursive()) {
+                break;
+            } else {
+                // disallow re-lock of a non-recursive lock
+                potential_self_deadlock_detected(locklocation, i.second, c);
+            }
         }
 
         std::pair<void *, void *> p1 = std::make_pair(i.first, c);
-        if (lockdata.lockorders.count(p1)) {
+        if ( ! lockdata.lockorders.try_emplace(p1, g_lockstack).second) {
             continue;
         }
-        lockdata.lockorders.emplace(p1, g_lockstack);
 
         std::pair<void *, void *> p2 = std::make_pair(c, i.first);
         lockdata.invlockorders.insert(p2);
         if (lockdata.lockorders.count(p2)) {
-            potential_deadlock_detected(p1, lockdata.lockorders[p2],
-                                        lockdata.lockorders[p1]);
+            potential_deadlock_detected(p1, lockdata.lockorders[p1], lockdata.lockorders[p2]);
         }
     }
+
+    // Try to find cycles where:
+    // Thread1: Locks A, B
+    // Thread2: Locks B, C
+    // Thread3: Locks C, A
+    std::set<void *> seen;
+    std::function<void(void *)> Recurse = [&](void *cur) {
+        if ( ! seen.insert(cur).second) return;
+        // If the lock `c` is an "ancestor" of itself, then we have detected a deadlock cycle.
+        // Note: the way the first loop above is written, a recursive lock will never be modeled
+        // as its own ancestor under normal, non-deadlocking usage patterns.
+        for (void *parent : lockdata.getParentsOf(cur)) {
+            if (lockdata.getParentsOf(parent).count(c)) {
+                potential_deadlock_cycle_detected(locklocation, parent, cur, c);
+            }
+            Recurse(parent);
+        }
+    };
+    Recurse(c);
 }
 
 static void pop_lock() {
     g_lockstack.pop_back();
 }
 
-void EnterCritical(const char* pszName, const char* pszFile, int nLine, void* cs, bool fTry)
+void EnterCritical(const char* pszName, const char* pszFile, int nLine, void *cs, bool fTry, bool fRecursive)
 {
-    push_lock(cs, CLockLocation(pszName, pszFile, nLine, fTry, util::ThreadGetInternalName()));
+    try {
+        push_lock(cs, CLockLocation(pszName, pszFile, nLine, fTry, util::ThreadGetInternalName(), fRecursive));
+    } catch (const PotentialDeadlockError &) {
+        // we must undo the lock stack push since the lock won't be acquired (this fixes unit tests)
+        pop_lock();
+        throw;
+    }
+}
+
+void CheckLastCritical(void *cs, std::string &lockname, const char *guardname,
+                       const char *file, int line) {
+    if (!g_lockstack.empty()) {
+        const auto &lastlock = g_lockstack.back();
+        if (lastlock.first == cs) {
+            lockname = lastlock.second.Name();
+            return;
+        }
+    }
+    throw std::system_error(
+        EPERM, std::generic_category(),
+        strprintf("%s:%s %s was not most recent critical section locked", file,
+                  line, guardname));
 }
 
 void LeaveCritical() {
@@ -217,5 +321,6 @@ void DeleteLock(void *cs) {
 }
 
 bool g_debug_lockorder_abort = true;
+PotentialDeadlockError::~PotentialDeadlockError() {}
 
 #endif /* DEBUG_LOCKORDER */
```

### src/sync.h
```diff
@@ -10,7 +10,12 @@
 
 #include <condition_variable>
 #include <mutex>
+#include <shared_mutex>
+#include <stdexcept>
+#include <string>
 #include <thread>
+#include <type_traits>
+#include <utility>
 
 /////////////////////////////////////////////////
 //                                             //
@@ -19,18 +24,31 @@
 /////////////////////////////////////////////////
 
 /*
+
+Mutex mutex;
+    std::mutex mutex;
+
+SharedMutex mutex;
+    std::shared_mutex mutex;
+
 RecursiveMutex mutex;
     std::recursive_mutex mutex;
 
 LOCK(mutex);
-    std::unique_lock<std::recursive_mutex> criticalblock(mutex);
+    std::unique_lock criticalblock(mutex);
+
+LOCK_SHARED(mutex);
+    std::shared_lock<std::shared_mutex> criticalblock(mutex);
 
 LOCK2(mutex1, mutex2);
-    std::unique_lock<std::recursive_mutex> criticalblock1(mutex1);
-    std::unique_lock<std::recursive_mutex> criticalblock2(mutex2);
+    std::unique_lock criticalblock1(mutex1);
+    std::unique_lock criticalblock2(mutex2);
 
 TRY_LOCK(mutex, name);
-    std::unique_lock<std::recursive_mutex> name(mutex, std::try_to_lock_t);
+    std::unique_lock< name(mutex, std::try_to_lock_t);
+
+TRY_LOCK_SHARED(mutex, name);
+    std::shared_lock<std::shared_mutex> name(mutex, std::try_to_lock_t);
 
 ENTER_CRITICAL_SECTION(mutex); // no RAII
     mutex.lock();
@@ -47,8 +65,10 @@ LEAVE_CRITICAL_SECTION(mutex); // no RAII
 
 #ifdef DEBUG_LOCKORDER
 void EnterCritical(const char *pszName, const char *pszFile, int nLine,
-                   void *cs, bool fTry = false);
+                   void *cs, bool fTry = false, bool fRecursive = false);
 void LeaveCritical();
+void CheckLastCritical(void *cs, std::string &lockname, const char *guardname,
+                       const char *file, int line);
 std::string LocksHeld();
 void AssertLockHeldInternal(const char *pszName, const char *pszFile, int nLine,
                             void *cs) ASSERT_EXCLUSIVE_LOCK(cs);
@@ -62,10 +82,27 @@ void DeleteLock(void *cs);
  * set to false in DEBUG_LOCKORDER unit tests.
  */
 extern bool g_debug_lockorder_abort;
+
+/**
+ *  This exception is thrown if g_debug_lockorder_abort == false, and if there
+ *  is a potential deadlock detected in LOCK() and friends.
+ */
+struct PotentialDeadlockError : std::logic_error {
+    using LockPtrPair = std::pair<void *, void *>;
+    PotentialDeadlockError(const char *message, const LockPtrPair &prev, const LockPtrPair &cur)
+        : std::logic_error(message), prevOrder(prev), curOrder(cur) {}
+    ~PotentialDeadlockError();
+
+    LockPtrPair prevOrder; ///< addresses of the mismatching locks (in the order previously seen)
+    LockPtrPair curOrder; ///< addresses of the mismatching locks (in the order as currently encountered)
+};
 #else
 static inline void EnterCritical(const char *pszName, const char *pszFile,
-                                 int nLine, void *cs, bool fTry = false) {}
+                                 int nLine, void *cs, bool fTry = false, bool fRecursive = false) {}
 static inline void LeaveCritical() {}
+static inline void CheckLastCritical(void *cs, std::string &lockname,
+                                     const char *guardname, const char *file,
+                                     int line) {}
 static inline void AssertLockHeldInternal(const char *pszName,
                                           const char *pszFile, int nLine,
                                           void *cs) ASSERT_EXCLUSIVE_LOCK(cs) {}
@@ -82,8 +119,9 @@ static inline void DeleteLock(void *cs) {}
  * Template mixin that adds -Wthread-safety locking annotations and lock order
  * checking to a subset of the mutex API.
  */
-template <typename PARENT> class LOCKABLE AnnotatedMixin : public PARENT {
-public:
+template <typename PARENT> struct LOCKABLE AnnotatedMixin : PARENT {
+    static constexpr bool recursive = std::is_base_of_v<std::recursive_mutex, PARENT>;
+
     ~AnnotatedMixin() { DeleteLock((void *)this); }
 
     void lock() EXCLUSIVE_LOCK_FUNCTION() { PARENT::lock(); }
@@ -97,25 +135,34 @@ template <typename PARENT> class LOCKABLE AnnotatedMixin : public PARENT {
     using UniqueLock = std::unique_lock<PARENT>;
 };
 
+template <typename PARENT> struct LOCKABLE AnnotatedSharedMixin : AnnotatedMixin<PARENT> {
+    void lock_shared() SHARED_LOCK_FUNCTION() { PARENT::lock_shared(); }
+    void unlock_shared() UNLOCK_FUNCTION() { PARENT::unlock_shared(); }
+    bool try_lock_shared() SHARED_TRYLOCK_FUNCTION(true) { return PARENT::try_lock_shared(); }
+    using SharedLock = std::shared_lock<PARENT>;
+};
+
 /**
  * Wrapped mutex: supports recursive locking, but no waiting
  * TODO: We should move away from using the recursive lock by default.
  */
 using RecursiveMutex = AnnotatedMixin<std::recursive_mutex>;
 
 /** Wrapped mutex: supports waiting but not recursive locking */
-typedef AnnotatedMixin<std::mutex> Mutex;
+using Mutex = AnnotatedMixin<std::mutex>;
+
+/** Wrapped shared_mutex: supports multiple readers, one writer (read-write locking) */
+using SharedMutex = AnnotatedSharedMixin<std::shared_mutex>;
 
 #ifdef DEBUG_LOCKCONTENTION
 void PrintLockContention(const char *pszName, const char *pszFile, int nLine);
 #endif
 
-/** Wrapper around std::unique_lock style lock for Mutex. */
-template <typename Mutex, typename Base = typename Mutex::UniqueLock>
-class SCOPED_LOCKABLE UniqueLock : public Base {
-private:
+/** Mixin class that does the low-level work of notifying our lock debug system. Base of: SharedLock and UniqueLock. */
+template <typename Base, bool recursive>
+class EnterMixin : public Base {
     void Enter(const char *pszName, const char *pszFile, int nLine) {
-        EnterCritical(pszName, pszFile, nLine, (void *)(Base::mutex()));
+        EnterCritical(pszName, pszFile, nLine, (void *)(Base::mutex()), false /* try */, recursive);
 #ifdef DEBUG_LOCKCONTENTION
         if (!Base::try_lock()) {
             PrintLockContention(pszName, pszFile, nLine);
@@ -127,17 +174,16 @@ class SCOPED_LOCKABLE UniqueLock : public Base {
     }
 
     bool TryEnter(const char *pszName, const char *pszFile, int nLine) {
-        EnterCritical(pszName, pszFile, nLine, (void *)(Base::mutex()), true);
+        EnterCritical(pszName, pszFile, nLine, (void *)(Base::mutex()), true /* try */, recursive);
         Base::try_lock();
         if (!Base::owns_lock()) {
             LeaveCritical();
         }
         return Base::owns_lock();
     }
 
-public:
-    UniqueLock(Mutex &mutexIn, const char *pszName, const char *pszFile,
-               int nLine, bool fTry = false) EXCLUSIVE_LOCK_FUNCTION(mutexIn)
+protected:
+    EnterMixin(typename Base::mutex_type &mutexIn, const char *pszName, const char *pszFile, int nLine, bool fTry)
         : Base(mutexIn, std::defer_lock) {
         if (fTry) {
             TryEnter(pszName, pszFile, nLine);
@@ -146,50 +192,110 @@ class SCOPED_LOCKABLE UniqueLock : public Base {
         }
     }
 
-    UniqueLock(Mutex *pmutexIn, const char *pszName, const char *pszFile,
-               int nLine, bool fTry = false) EXCLUSIVE_LOCK_FUNCTION(pmutexIn) {
-        if (!pmutexIn) {
-            return;
-        }
-
-        *static_cast<Base *>(this) = Base(*pmutexIn, std::defer_lock);
-        if (fTry) {
-            TryEnter(pszName, pszFile, nLine);
-        } else {
-            Enter(pszName, pszFile, nLine);
-        }
-    }
-
-    ~UniqueLock() UNLOCK_FUNCTION() {
+    ~EnterMixin() {
         if (Base::owns_lock()) {
             LeaveCritical();
         }
     }
 
+public:
     operator bool() { return Base::owns_lock(); }
+
+protected:
+    // needed for reverse_lock
+    EnterMixin() {}
+
+public:
+    /**
+     * An RAII-style reverse lock. Unlocks on construction and locks on
+     * destruction.
+     */
+    class reverse_lock {
+        EnterMixin &lock;
+        EnterMixin templock;
+        std::string lockname;
+        const std::string file;
+        const int line;
+
+    public:
+        explicit reverse_lock(EnterMixin &_lock, const char *_guardname,
+                              const char *_file, int _line)
+            : lock(_lock), file(_file), line(_line) {
+            CheckLastCritical((void *)lock.mutex(), lockname, _guardname, _file,
+                              _line);
+            lock.unlock();
+            LeaveCritical();
+            lock.swap(templock);
+        }
+
+        reverse_lock(reverse_lock const&) = delete;
+        reverse_lock& operator=(reverse_lock const&) = delete;
+
+        ~reverse_lock() {
+            templock.swap(lock);
+            EnterCritical(lockname.c_str(), file.c_str(), line,
+                          (void *)lock.mutex(), false /* try */, recursive);
+            lock.lock();
+        }
+    };
+    friend class reverse_lock;
+};
+
+#define REVERSE_LOCK(g)                                                        \
+    decltype(g)::reverse_lock PASTE2(revlock, __COUNTER__)(g, #g, __FILE__,    \
+                                                           __LINE__)
+
+/** Wrapper around std::unique_lock style lock for Mutex. */
+template <typename Mutex, typename Base = typename Mutex::UniqueLock>
+struct SCOPED_LOCKABLE UniqueLock : EnterMixin<Base, Mutex::recursive> {
+    UniqueLock(Mutex &mutexIn, const char *pszName, const char *pszFile,
+               int nLine, bool fTry = false) EXCLUSIVE_LOCK_FUNCTION(mutexIn)
+        : EnterMixin<Base, Mutex::recursive>(mutexIn, pszName, pszFile, nLine, fTry) {}
+
+    ~UniqueLock() UNLOCK_FUNCTION() {}
+};
+
+/** Wrapper around std::shared_lock style lock for SharedMutex. */
+template <typename SharedMutex, typename Base = typename SharedMutex::SharedLock>
+struct SCOPED_LOCKABLE SharedLock : EnterMixin<Base, SharedMutex::recursive> {
+    SharedLock(SharedMutex &mutexIn, const char *pszName, const char *pszFile,
+               int nLine, bool fTry = false) SHARED_LOCK_FUNCTION(mutexIn)
+        : EnterMixin<Base, SharedMutex::recursive>(mutexIn, pszName, pszFile, nLine, fTry) {}
+
+    ~SharedLock() UNLOCK_FUNCTION() {}
 };
 
 template <typename MutexArg>
-using DebugLock = UniqueLock<typename std::remove_reference<
-    typename std::remove_pointer<MutexArg>::type>::type>;
+using DebugLock = UniqueLock<std::remove_reference_t<std::remove_pointer_t<MutexArg>>>;
+
+template <typename SharedMutexArg>
+using DebugSharedLock = SharedLock<std::remove_reference_t<std::remove_pointer_t<SharedMutexArg>>>;
 
 #define PASTE(x, y) x##y
 #define PASTE2(x, y) PASTE(x, y)
 
 #define LOCK(cs)                                                               \
-    DebugLock<decltype(cs)> PASTE2(criticalblock,                              \
-                                   __COUNTER__)(cs, #cs, __FILE__, __LINE__)
+    DebugLock<decltype(cs)> PASTE2(criticalblock, __COUNTER__)                 \
+                                (cs, #cs, __FILE__, __LINE__)
+#define LOCK_SHARED(cs)                                                        \
+    DebugSharedLock<decltype(cs)> PASTE2(criticalblock, __COUNTER__)           \
+                                      (cs, #cs, __FILE__, __LINE__)
 #define LOCK2(cs1, cs2)                                                        \
     DebugLock<decltype(cs1)> criticalblock1(cs1, #cs1, __FILE__, __LINE__);    \
     DebugLock<decltype(cs2)> criticalblock2(cs2, #cs2, __FILE__, __LINE__);
 #define TRY_LOCK(cs, name)                                                     \
     DebugLock<decltype(cs)> name(cs, #cs, __FILE__, __LINE__, true)
+#define TRY_LOCK_SHARED(cs, name)                                              \
+    DebugSharedLock<decltype(cs)> name(cs, #cs, __FILE__, __LINE__, true)
 #define WAIT_LOCK(cs, name)                                                    \
     DebugLock<decltype(cs)> name(cs, #cs, __FILE__, __LINE__)
+#define WAIT_LOCK_SHARED(cs, name)                                             \
+    DebugSharedLock<decltype(cs)> name(cs, #cs, __FILE__, __LINE__)
 
 #define ENTER_CRITICAL_SECTION(cs)                                             \
     {                                                                          \
-        EnterCritical(#cs, __FILE__, __LINE__, (void *)(&cs));                 \
+        EnterCritical(#cs, __FILE__, __LINE__, (void *)(&cs),                  \
+                      false /* try */, (cs).recursive);                        \
         (cs).lock();                                                           \
     }
 
@@ -225,7 +331,6 @@ using DebugLock = UniqueLock<typename std::remove_reference<
 #define WITH_LOCK(cs, code) [&]() -> decltype(auto) { LOCK(cs); code; }()
 
 class CSemaphore {
-private:
     std::condition_variable condition;
     std::mutex mutex;
     int value;
@@ -259,7 +364,6 @@ class CSemaphore {
 
 /** RAII-style semaphore lock */
 class CSemaphoreGrant {
-private:
     CSemaphore *sem;
     bool fHaveGrant;
 
```

### src/test/CMakeLists.txt
```diff
@@ -121,6 +121,7 @@ add_boost_unit_tests_to_suite(bitcoin test_bitcoin
 		crypto_tests.cpp
 		cuckoocache_tests.cpp
 		dbwrapper_tests.cpp
+		deadlock_tests.cpp
 		denialofservice_tests.cpp
 		descriptor_tests.cpp
 		dsproof_dspidptr_tests.cpp
```

### src/test/deadlock_tests.cpp
```diff
@@ -0,0 +1,611 @@
+// Copyright (c) 2019 Greg Griffith
+// Copyright (c) 2019-2020 The Bitcoin Unlimited developers
+// Copyright (c) 2021 The Bitcoin developers
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <sync.h>
+#include <test/setup_common.h>
+#include <util/time.h>
+
+#include <boost/test/unit_test.hpp>
+
+#include <atomic>
+#include <memory>
+#include <optional>
+#include <thread>
+
+// The below code explicitly deadlocks in order to test the deadlock detector.
+// This leads to false positives for thread sanitizers. So we disable this test
+// if compiling with -fsanitize=thread.
+#if defined(__SANITIZE_THREAD__)
+#  define SKIP_SANITIZER_NOT_SUPPORTED
+#elif defined(__has_feature)
+#  if __has_feature(thread_sanitizer)
+#    define SKIP_SANITIZER_NOT_SUPPORTED
+#  endif
+#endif
+
+BOOST_FIXTURE_TEST_SUITE(deadlock_tests, BasicTestingSetupWithDeadlockExceptions)
+
+#if defined(DEBUG_LOCKORDER) && !defined(SKIP_SANITIZER_NOT_SUPPORTED) // this ifdef covers the bulk of this file
+
+#ifdef __clang__
+#pragma clang diagnostic push
+#pragma clang diagnostic ignored "-Wthread-safety-analysis"
+#endif
+
+#if defined(__GNUC__) && (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 6))
+// GCC warns excessively about shadowed variable names, which we use in lambdas in
+// this test for clarity. So disable that warning.
+#pragma GCC diagnostic push
+#pragma GCC diagnostic ignored "-Wshadow"
+#endif
+
+// shared lock a shared mutex
+// then try to exclusive lock the same shared mutex while holding shared lock,
+// should self deadlock
+BOOST_AUTO_TEST_CASE(test1) {
+    SharedMutex shared_mutex;
+    LOCK_SHARED(shared_mutex);
+    BOOST_CHECK_THROW(LOCK(shared_mutex), PotentialDeadlockError);
+}
+
+
+// RecursiveMutex version of test1 (self deadlock should not be tripped up here)
+BOOST_AUTO_TEST_CASE(test1r) {
+    RecursiveMutex mutex;
+    LOCK(mutex);
+    BOOST_CHECK_NO_THROW(LOCK(mutex));
+}
+
+
+// exclusive lock a shared mutex
+// then try to shared lock the same shared mutex while holding the exclusive
+// lock, should self deadlock
+BOOST_AUTO_TEST_CASE(test2) {
+    SharedMutex shared_mutex;
+    LOCK(shared_mutex);
+    BOOST_CHECK_THROW(LOCK_SHARED(shared_mutex), PotentialDeadlockError);
+}
+
+
+// shared lock a shared mutex
+// then try to shared lock the same shared mutex while holding the original
+// shared lock, should self deadlock, no recursion allowed in a shared mutex
+BOOST_AUTO_TEST_CASE(test3) {
+    SharedMutex shared_mutex;
+    LOCK_SHARED(shared_mutex);
+    BOOST_CHECK_THROW(LOCK_SHARED(shared_mutex), PotentialDeadlockError);
+}
+
+
+// exclusive lock a shared mutex
+// then try to exclusive likc the same shared mutex while holding the original
+// exclusive lock, should self deadlock, no recursion allowed in a shared mutex
+BOOST_AUTO_TEST_CASE(test4) {
+    SharedMutex shared_mutex;
+    LOCK(shared_mutex);
+    BOOST_CHECK_THROW(LOCK(shared_mutex), PotentialDeadlockError);
+}
+
+
+// 2 shared mutex lock themselves then try to
+// shared lock each other
+// this should deadlock and throw an exception
+// We use a "global" (static) shared mutex here.
+BOOST_AUTO_TEST_CASE(test5) {
+    static SharedMutex mutexA;
+    static SharedMutex mutexB;
+    struct Context {
+        std::atomic<bool> done{false};
+        std::atomic<int> lock_exceptions{0};
+        std::atomic<int> writelocks{0};
+    };
+    using SharedCtx = std::shared_ptr<Context>;
+    SharedCtx ctx = std::make_shared<Context>();
+
+    auto TestThread1 = [](SharedCtx ctx){
+        LOCK(mutexA);
+        ++ctx->writelocks;
+        while (ctx->writelocks != 2) ;
+        try {
+            LOCK_SHARED(mutexB);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto TestThread2 = [](SharedCtx ctx){
+        LOCK(mutexB);
+        ++ctx->writelocks;
+        while (ctx->writelocks != 2) ;
+        try {
+            LOCK_SHARED(mutexA);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    std::thread thread1(TestThread1, ctx);
+    std::thread thread2(TestThread2, ctx);
+    Tic elapsed;
+    while (!ctx->lock_exceptions && elapsed.secs() < 5) ; // wait for predicate or 5 seconds, whichever is sooner
+    ctx->done = true;
+    if (ctx->lock_exceptions != 1) {
+        // test failure -- detach threads in this case so process can proceed without hanging
+        thread1.detach();
+        thread2.detach();
+    } else {
+        thread1.join();
+        thread2.join();
+    }
+    BOOST_CHECK(ctx->lock_exceptions == 1);
+}
+
+
+// two shared mutex (A, B)
+// thread1 lock_shared A,
+// thread2 lock B
+// thread1 lock_shared B
+// thread2 lock A, should deadlock here
+// because thread1 is holding a shared lock on A and is waiting for B
+// while thread2 is holding an exclusive lock on B and is waiting for A
+BOOST_AUTO_TEST_CASE(test6) {
+    struct Context {
+        SharedMutex mutexA;
+        SharedMutex mutexB;
+        std::atomic<bool> done{false};
+        std::atomic<int> lock_exceptions{0};
+        std::atomic<int> writelocks{0};
+        std::atomic<int> readlocks{0};
+    };
+    using SharedCtx = std::shared_ptr<Context>;
+    SharedCtx ctx = std::make_shared<Context>();
+
+    auto Thread1 = [](SharedCtx ctx){
+        LOCK_SHARED(ctx->mutexA);
+        ++ctx->readlocks;
+        while (ctx->writelocks != 1) ;
+        try {
+            LOCK_SHARED(ctx->mutexB);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread2 = [](SharedCtx ctx){
+        while (ctx->readlocks != 1) ;
+        LOCK(ctx->mutexB);
+        ++ctx->writelocks;
+        try {
+            LOCK(ctx->mutexA);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    std::thread thread1(Thread1, ctx);
+    std::thread thread2(Thread2, ctx);
+    Tic elapsed;
+    while (!ctx->lock_exceptions && elapsed.secs() < 5) ; // wait for predicate or 5 seconds, whichever is sooner
+    ctx->done = true;
+    if (ctx->lock_exceptions != 1) {
+        // test failure -- detach threads in this case so process can proceed without hanging
+        thread1.detach();
+        thread2.detach();
+    } else {
+        thread1.join();
+        thread2.join();
+    }
+    BOOST_CHECK(ctx->lock_exceptions == 1);
+}
+
+
+// Threads 1 2 3 and shared mutex A B C
+// Thread1 lock_shared A
+// Thread2 lock_shared B
+// Thread3 lock_shared C
+// Thread1 lock B
+// Thread2 lock C
+// Thread3 lock A
+// This tests locking race conditions as well as 3 way and higher lock ordering issues,
+// the test is not specific on which thread will deadlock when trying to exclusively lock
+// the above indicated shared mutex but one of them will.
+BOOST_AUTO_TEST_CASE(test7) {
+    struct Context {
+        SharedMutex mutexA;
+        SharedMutex mutexB;
+        SharedMutex mutexC;
+
+        std::atomic<bool> done{false};
+        std::atomic<int> lock_exceptions{0};
+        std::atomic<int> readlocks{0};
+    };
+    using SharedCtx = std::shared_ptr<Context>;
+    SharedCtx ctx = std::make_shared<Context>();
+
+    auto Thread1 = [](SharedCtx ctx){
+        LOCK_SHARED(ctx->mutexA); // 1
+        ++ctx->readlocks;
+        while (ctx->readlocks != 3) ;
+        try {
+            LOCK(ctx->mutexB);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread2 = [](SharedCtx ctx) {
+        while (ctx->readlocks != 1) ;
+        LOCK_SHARED(ctx->mutexB); // 2
+        ++ctx->readlocks;
+        while (ctx->readlocks != 3) ;
+        try {
+            LOCK(ctx->mutexC);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread3 = [](SharedCtx ctx){
+        while (ctx->readlocks != 2) ;
+        LOCK_SHARED(ctx->mutexC); // 3
+        ++ctx->readlocks;
+        while (ctx->readlocks != 3) ;
+        try {
+            LOCK(ctx->mutexA);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    std::thread thread1(Thread1, ctx);
+    std::thread thread2(Thread2, ctx);
+    std::thread thread3(Thread3, ctx);
+    Tic elapsed;
+    while (!ctx->lock_exceptions && elapsed.secs() < 5) ;
+    ctx->done = true;
+    if (ctx->lock_exceptions != 1) {
+        // test failure -- detach threads in this case so process can proceed without hanging
+        thread1.detach();
+        thread2.detach();
+        thread3.detach();
+    } else {
+        thread1.join();
+        thread2.join();
+        thread3.join();
+    }
+    BOOST_CHECK(ctx->lock_exceptions == 1);
+}
+
+
+// Threads 1 2 3 and shared mutex A B C
+// Thread1 lock A
+// Thread2 lock B
+// Thread3 lock C
+// Thread1 lock_shared B
+// Thread2 lock_shared C
+// Thread3 lock_shared A
+// This tests locking race conditions as well as 3 way and higher lock ordering issues,
+// the test is not specific on which thread will deadlock when trying to shared lock
+// the above indicated shared mutex but one of them will.
+BOOST_AUTO_TEST_CASE(test8) {
+    struct Context {
+        SharedMutex mutexA;
+        SharedMutex mutexB;
+        SharedMutex mutexC;
+
+        std::atomic<bool> done{false};
+        std::atomic<int> lock_exceptions{0};
+        std::atomic<int> writelocks{0};
+    };
+    using SharedCtx = std::shared_ptr<Context>;
+    SharedCtx ctx = std::make_shared<Context>();
+
+    auto Thread1 = [](SharedCtx ctx){
+        LOCK(ctx->mutexA); // 1
+        ++ctx->writelocks;
+        while (ctx->writelocks != 3) ;
+        try {
+            LOCK_SHARED(ctx->mutexB);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread2 = [](SharedCtx ctx){
+        while (ctx->writelocks != 1) ;
+        LOCK(ctx->mutexB); // 2
+        ++ctx->writelocks;
+        while (ctx->writelocks != 3) ;
+        try {
+            LOCK_SHARED(ctx->mutexC);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread3 = [](SharedCtx ctx){
+        while (ctx->writelocks != 2) ;
+        LOCK(ctx->mutexC);
+        ++ctx->writelocks;
+        while (ctx->writelocks != 3) ;
+        try {
+            LOCK_SHARED(ctx->mutexA);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    std::thread thread1(Thread1, ctx);
+    std::thread thread2(Thread2, ctx);
+    std::thread thread3(Thread3, ctx);
+    while (!ctx->lock_exceptions) ;
+    ctx->done = true;
+    if (ctx->lock_exceptions != 1) {
+        // test failure -- detach threads in this case so process can proceed without hanging
+        thread1.detach();
+        thread2.detach();
+        thread3.detach();
+    } else {
+        thread1.join();
+        thread2.join();
+        thread3.join();
+    }
+    BOOST_CHECK(ctx->lock_exceptions == 1);
+}
+
+
+// Identical to test8, but uses a RecursiveMutex instead (deadlock should still be detected)
+BOOST_AUTO_TEST_CASE(test8r) {
+    struct Context {
+        RecursiveMutex mutexA;
+        RecursiveMutex mutexB;
+        RecursiveMutex mutexC;
+
+        std::atomic<bool> done{false};
+        std::atomic<int> lock_exceptions{0};
+        std::atomic<int> writelocks{0};
+    };
+    using SharedCtx = std::shared_ptr<Context>;
+    SharedCtx ctx = std::make_shared<Context>();
+
+    auto Thread1 = [](SharedCtx ctx){
+        LOCK(ctx->mutexA); // 1
+        ++ctx->writelocks;
+        while (ctx->writelocks != 3) ;
+        try {
+            LOCK(ctx->mutexB);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread2 = [](SharedCtx ctx){
+        while (ctx->writelocks != 1) ;
+        LOCK(ctx->mutexB); // 2
+        ++ctx->writelocks;
+        while (ctx->writelocks != 3) ;
+        try {
+            LOCK(ctx->mutexC);
+        } catch (const PotentialDeadlockError&) {
+            ctx->lock_exceptions++;
+        }
+        while (!ctx->done) ;
+    };
+
+    auto Thread3 = [](SharedCtx ctx){
+        while (ctx->writelocks != 2) ;
+        LOCK(ctx->mutexC);
+        ++ctx->writelocks;
+        while (ctx->writelocks != 3) ;
+        try {
+            LOCK(ctx->mutexA);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+
+    std::thread thread1(Thread1, ctx);
+    std::thread thread2(Thread2, ctx);
+    std::thread thread3(Thread3, ctx);
+    Tic elapsed;
+    while (!ctx->lock_exceptions && elapsed.secs() < 5) ;
+    ctx->done = true;
+    if (ctx->lock_exceptions != 1) {
+        // test failure -- detach threads in this case so process can proceed without hanging
+        thread1.detach();
+        thread2.detach();
+        thread3.detach();
+    } else {
+        thread1.join();
+        thread2.join();
+        thread3.join();
+    }
+    BOOST_CHECK(ctx->lock_exceptions == 1);
+}
+
+
+// 2 shared mutex lock themselves then try to
+// shared lock each other
+// this should deadlock and throw an exception
+// this is the same as test 5 but we are using pointers to mutex
+// instead of global mutex, this is an important difference
+BOOST_AUTO_TEST_CASE(test9) {
+    struct Context {
+        SharedMutex mutex[2];
+        std::atomic<bool> done{false};
+        std::atomic<int> lock_exceptions{0};
+        std::atomic<int> writelocks{0};
+    };
+    using SharedCtx = std::shared_ptr<Context>;
+    SharedCtx ctx = std::make_shared<Context>();
+
+    auto TestThread = [](SharedCtx ctx, SharedMutex *mutexA, SharedMutex *mutexB) {
+        LOCK(*mutexA);
+        ++ctx->writelocks;
+        while (ctx->writelocks != 2) ;
+        try {
+            LOCK_SHARED(*mutexB);
+        } catch (const PotentialDeadlockError&) {
+            ++ctx->lock_exceptions;
+        }
+        while (!ctx->done) ;
+    };
+    std::thread thread1(TestThread, ctx, &ctx->mutex[0], &ctx->mutex[1]);
+    std::thread thread2(TestThread, ctx, &ctx->mutex[1], &ctx->mutex[0]);
+    Tic elapsed;
+    while (!ctx->lock_exceptions && elapsed.secs() < 5) ;
+    ctx->done = true;
+    if (ctx->lock_exceptions != 1) {
+        // test failure -- detach threads in this case so process can proceed without hanging
+        thread1.detach();
+        thread2.detach();
+    } else {
+        thread1.join();
+        thread2.join();
+    }
+    BOOST_CHECK(ctx->lock_exceptions == 1);
+}
+
+
+// a very basic test to test lock order history tracking
+// this should error because a different lock ordering was previously seen
+BOOST_AUTO_TEST_CASE(test10) {
+    SharedMutex mutexA;
+    SharedMutex mutexB;
+
+    auto Thread1 = [&]{
+        LOCK(mutexA);
+        LOCK(mutexB);
+    };
+
+    std::atomic_bool didThrow{false};
+    auto Thread2 = [&]{
+        LOCK(mutexB);
+        try {
+            LOCK(mutexA);
+        } catch (const PotentialDeadlockError &) {
+            didThrow = true;
+        }
+    };
+
+    std::thread thread1(Thread1);
+    thread1.join();
+    std::thread thread2(Thread2);
+    thread2.join();
+    BOOST_CHECK(didThrow);
+}
+
+// RecursiveMutex version of test10
+// this should error because a different lock ordering was previously seen
+BOOST_AUTO_TEST_CASE(test10r) {
+    RecursiveMutex mutexA;
+    RecursiveMutex mutexB;
+
+    auto Thread1 = [&]{
+        LOCK(mutexA);
+        LOCK(mutexB);
+    };
+
+    std::atomic_bool didThrow{false};
+    auto Thread2 = [&]{
+        LOCK(mutexB);
+        try {
+            LOCK(mutexA);
+        } catch (const PotentialDeadlockError &) {
+            didThrow = true;
+        }
+    };
+
+    std::thread thread1(Thread1);
+    thread1.join();
+    std::thread thread2(Thread2);
+    thread2.join();
+    BOOST_CHECK(didThrow);
+}
+
+// A test helper that checks that destroying a lock and creating another one
+// in the same memory location should lead to a situation where there *is* no
+// deadlock detected.  This is because on lock destruction, lock histories
+// should be cleared for that lock (since it's "going away"!).
+template <typename MutexT>
+void test11_generic() {
+    std::optional<MutexT> mutexA;
+    std::optional<MutexT> mutexB;
+
+    for (auto *lockPtr : {&mutexA, &mutexB}) {
+        // (Re)construct locks (wipe history for this run)
+        mutexA.emplace();
+        mutexB.emplace();
+
+        auto Thread1 = [&]{
+            LOCK(mutexA.value());
+            LOCK(mutexB.value());
+        };
+
+        std::atomic_bool didThrow{false};
+        auto Thread2 = [&]{
+            LOCK(mutexB.value());
+            try {
+                LOCK(mutexA.value());
+            } catch (const PotentialDeadlockError &) {
+                didThrow = true;
+            }
+        };
+
+        std::thread thread1(Thread1);
+        thread1.join();
+
+        // Now, delete and recreate one of the locks at the same memory
+        // location (lock history for it should be wiped).
+        lockPtr->reset();
+        lockPtr->emplace();
+
+        // Even though we are locking B then A in the below thread, one of
+        // them is "new" (was reconstructed above) and thus it has no
+        // lock order history, and so no deadlock should be detected.
+        std::thread thread2(Thread2);
+        thread2.join();
+
+        BOOST_CHECK(!didThrow);
+    }
+}
+
+BOOST_AUTO_TEST_CASE(test11) {
+    // Run the above test for all 3 lock types
+    test11_generic<RecursiveMutex>();
+    test11_generic<Mutex>();
+    test11_generic<SharedMutex>();
+}
+
+#if defined(__GNUC__) && (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 6))
+#pragma GCC diagnostic pop
+#endif
+
+#ifdef __clang__
+#pragma clang diagnostic pop
+#endif
+
+#else // !DEBUG_LOCKORDER || SKIP_SANITIZER_NOT_SUPPORTED
+
+BOOST_AUTO_TEST_CASE(empty_deadlock_tests) {
+    BOOST_CHECK("Compile in Debug mode (without sanitize=thread), to enable the deadlock_tests");
+}
+
+#endif
+
+BOOST_AUTO_TEST_SUITE_END()
```

### src/test/reverselock_tests.cpp
```diff
@@ -2,7 +2,7 @@
 // Distributed under the MIT software license, see the accompanying
 // file COPYING or http://www.opensource.org/licenses/mit-license.php.
 
-#include <reverselock.h>
+#include <sync.h>
 
 #include <test/setup_common.h>
 
@@ -11,20 +11,49 @@
 BOOST_FIXTURE_TEST_SUITE(reverselock_tests, BasicTestingSetup)
 
 BOOST_AUTO_TEST_CASE(reverselock_basics) {
-    boost::mutex mutex;
-    boost::unique_lock<boost::mutex> lock(mutex);
+    Mutex mutex;
+    WAIT_LOCK(mutex, lock);
 
     BOOST_CHECK(lock.owns_lock());
     {
-        reverse_lock<boost::unique_lock<boost::mutex>> rlock(lock);
+        REVERSE_LOCK(lock);
         BOOST_CHECK(!lock.owns_lock());
     }
     BOOST_CHECK(lock.owns_lock());
 }
 
+BOOST_AUTO_TEST_CASE(reverselock_multiple) {
+    Mutex mutex2;
+    Mutex mutex;
+    WAIT_LOCK(mutex2, lock2);
+    WAIT_LOCK(mutex, lock);
+
+    // Make sure undoing two locks succeeds
+    {
+        REVERSE_LOCK(lock);
+        BOOST_CHECK(!lock.owns_lock());
+        REVERSE_LOCK(lock2);
+        BOOST_CHECK(!lock2.owns_lock());
+    }
+    BOOST_CHECK(lock.owns_lock());
+    BOOST_CHECK(lock2.owns_lock());
+}
+
 BOOST_AUTO_TEST_CASE(reverselock_errors) {
-    boost::mutex mutex;
-    boost::unique_lock<boost::mutex> lock(mutex);
+    Mutex mutex2;
+    Mutex mutex;
+    WAIT_LOCK(mutex2, lock2);
+    WAIT_LOCK(mutex, lock);
+
+#ifdef DEBUG_LOCKORDER
+    // Make sure trying to reverse lock a previous lock fails
+    try {
+        REVERSE_LOCK(lock2);
+        BOOST_CHECK(false); // REVERSE_LOCK(lock2) succeeded
+    } catch (...) {
+    }
+    BOOST_CHECK(lock2.owns_lock());
+#endif
 
     // Make sure trying to reverse lock an unlocked lock fails
     lock.unlock();
@@ -33,7 +62,7 @@ BOOST_AUTO_TEST_CASE(reverselock_errors) {
 
     bool failed = false;
     try {
-        reverse_lock<boost::unique_lock<boost::mutex>> rlock(lock);
+        REVERSE_LOCK(lock);
     } catch (...) {
         failed = true;
     }
@@ -48,7 +77,7 @@ BOOST_AUTO_TEST_CASE(reverselock_errors) {
     lock.lock();
     BOOST_CHECK(lock.owns_lock());
     {
-        reverse_lock<boost::unique_lock<boost::mutex>> rlock(lock);
+        REVERSE_LOCK(lock);
         BOOST_CHECK(!lock.owns_lock());
     }
 
```

### src/test/setup_common.cpp
```diff
@@ -28,6 +28,7 @@
 #include <script/scriptcache.h>
 #include <script/sigcache.h>
 #include <streams.h>
+#include <sync.h>
 #include <txdb.h>
 #include <txmempool.h>
 #include <ui_interface.h>
@@ -81,6 +82,27 @@ fs::path BasicTestingSetup::SetDataDir(const std::string &name) {
     return ret;
 }
 
+;
+/* static */ std::atomic_bool EnableDeadlockExceptionsMixin::saved_g_debug_lockorder_abort{false};
+/* static */ std::atomic_int EnableDeadlockExceptionsMixin::instance_ctr{0};
+
+EnableDeadlockExceptionsMixin::EnableDeadlockExceptionsMixin() noexcept {
+#ifdef DEBUG_LOCKORDER
+    if (instance_ctr++ == 0) {
+        saved_g_debug_lockorder_abort = g_debug_lockorder_abort;
+        g_debug_lockorder_abort = false;
+    }
+#endif
+}
+
+EnableDeadlockExceptionsMixin::~EnableDeadlockExceptionsMixin() {
+#ifdef DEBUG_LOCKORDER
+    if (--instance_ctr == 0) {
+        g_debug_lockorder_abort = saved_g_debug_lockorder_abort.load();
+    }
+#endif
+}
+
 TestingSetup::TestingSetup(const std::string &chainName)
     : BasicTestingSetup(chainName) {
     SetDataDir("tempdir");
```

### src/test/setup_common.h
```diff
@@ -15,6 +15,7 @@
 #include <random.h>
 #include <scheduler.h>
 
+#include <atomic>
 #include <type_traits>
 
 /**
@@ -87,6 +88,25 @@ struct BasicTestingSetup {
     const fs::path m_path_root;
 };
 
+/**
+ * @brief Helper mixin for struct BasicTestingSetupWithDeadlockExceptions
+ */
+struct EnableDeadlockExceptionsMixin {
+    EnableDeadlockExceptionsMixin() noexcept;
+    ~EnableDeadlockExceptionsMixin();
+protected:
+    static std::atomic_bool saved_g_debug_lockorder_abort;
+    static std::atomic_int instance_ctr;
+};
+
+/**
+ * @brief Testing setup whereby if we are compiled in Debug mode, will also make deadlock
+ * detection throw exceptions (rather than abort() the app).
+ */
+struct BasicTestingSetupWithDeadlockExceptions : BasicTestingSetup, EnableDeadlockExceptionsMixin {
+    using BasicTestingSetup::BasicTestingSetup;
+};
+
 /**
  * Testing setup that configures a complete environment.
  * Included are data directory, coins database, script check threads setup.
```

### src/test/sync_tests.cpp
```diff
@@ -4,9 +4,17 @@
 
 #include <sync.h>
 #include <test/setup_common.h>
+#include <util/defer.h>
 
 #include <boost/test/unit_test.hpp>
 
+#include <algorithm>
+#include <array>
+#include <atomic>
+#include <chrono>
+#include <thread>
+#include <vector>
+
 namespace {
 template <typename MutexType>
 void TestPotentialDeadLockDetected(MutexType &mutex1, MutexType &mutex2) {
@@ -16,6 +24,13 @@ void TestPotentialDeadLockDetected(MutexType &mutex1, MutexType &mutex2) {
         LOCK2(mutex2, mutex1);
     } catch (const std::logic_error &e) {
         BOOST_CHECK_EQUAL(e.what(), "potential deadlock detected");
+#ifdef DEBUG_LOCKORDER
+        auto &pe = dynamic_cast<const PotentialDeadlockError &>(e);
+        BOOST_CHECK_EQUAL(pe.prevOrder.first, static_cast<void *>(&mutex1));
+        BOOST_CHECK_EQUAL(pe.prevOrder.second, static_cast<void *>(&mutex2));
+        BOOST_CHECK_EQUAL(pe.curOrder.first, static_cast<void *>(&mutex2));
+        BOOST_CHECK_EQUAL(pe.curOrder.second, static_cast<void *>(&mutex1));
+#endif
         error_thrown = true;
     }
 #ifdef DEBUG_LOCKORDER
@@ -26,23 +41,83 @@ void TestPotentialDeadLockDetected(MutexType &mutex1, MutexType &mutex2) {
 }
 } // namespace
 
-BOOST_FIXTURE_TEST_SUITE(sync_tests, BasicTestingSetup)
+BOOST_FIXTURE_TEST_SUITE(sync_tests, BasicTestingSetupWithDeadlockExceptions)
 
 BOOST_AUTO_TEST_CASE(potential_deadlock_detected) {
-#ifdef DEBUG_LOCKORDER
-    bool prev = g_debug_lockorder_abort;
-    g_debug_lockorder_abort = false;
-#endif
-
     RecursiveMutex rmutex1, rmutex2;
     TestPotentialDeadLockDetected(rmutex1, rmutex2);
 
     Mutex mutex1, mutex2;
     TestPotentialDeadLockDetected(mutex1, mutex2);
 
-#ifdef DEBUG_LOCKORDER
-    g_debug_lockorder_abort = prev;
-#endif
+    SharedMutex shared1, shared2;
+    TestPotentialDeadLockDetected(shared1, shared2);
+}
+
+BOOST_AUTO_TEST_CASE(shared_mutex_tests) {
+    std::vector<std::thread> threads;
+    using namespace std::chrono_literals;
+    struct {
+        SharedMutex cs;
+        std::atomic_int shared_ct = 0;
+        int exclusive_ct GUARDED_BY(cs) = 0;
+    } s;
+
+    constexpr size_t max_predicates = 10; // update this if adding more subthreads to this test
+    std::array<bool, max_predicates> predicates;
+    for (auto &pred : predicates) pred = true; // start all predicates out as "vacuously true"
+
+    size_t thr_idx = 0;
+
+    threads.emplace_back([&s](bool *pred){
+        std::this_thread::sleep_for(40ms);
+        LOCK(s.cs);
+        ++s.exclusive_ct;
+        Defer d([&]{
+            AssertLockHeld(s.cs);
+            --s.exclusive_ct;
+        });
+        // cannot do BOOST_CHECK in a thread, so we must save predicate check value here
+        *pred = s.shared_ct.load() == 0;
+    }, &predicates.at(thr_idx++));
+    for (int i = 0; i < 8; ++i) {
+        threads.emplace_back([&s](bool *pred){
+            LOCK_SHARED(s.cs);
+            ++s.shared_ct;
+            Defer d([&]{ --s.shared_ct; });
+            // cannot do BOOST_CHECK in a thread, so we must save predicate check value here
+            *pred = s.exclusive_ct == 0;
+            std::this_thread::sleep_for(10ms);
+        }, &predicates.at(thr_idx++));
+    }
+    for (auto & thr : threads) {
+        thr.join();
+    }
+
+    // Additional test that multiple threads can lock shared, also
+    // test that REVERSE_LOCK works on a shared lock as expected,
+    // and that WAIT_LOCK_SHARED and TRY_LOCK_SHARED work as expected.
+    SharedMutex sm;
+    WAIT_LOCK_SHARED(sm, lock);
+    BOOST_CHECK(lock.owns_lock());
+    // ensure a second thread can acquire shared
+    std::thread([&sm](bool *pred){
+        TRY_LOCK_SHARED(sm, lock2);
+        *pred = lock2.owns_lock();
+        if (lock2.owns_lock()){
+            // also check that reverse lock works ok
+            REVERSE_LOCK(lock2);
+            *pred = !lock2.owns_lock() && *pred;
+        }
+        *pred = lock2.owns_lock() && *pred;
+    }, &predicates.at(thr_idx++)).join();
+
+    BOOST_CHECK(thr_idx <= max_predicates);
+
+    // Check that all predicates (which were assigned to a sub-thread) are true
+    // Note again: we cannot do BOOST_CHECK in a subthread which is why we must do this.
+    BOOST_CHECK(std::all_of(predicates.begin(), predicates.begin() + thr_idx,
+                            [](bool pred) { return pred; }));
 }
 
 BOOST_AUTO_TEST_SUITE_END()
```
