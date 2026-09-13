# [H] PraisonAI Slack app_mention bypasses configured user/channel authorization

## Summary
Severity: High
Advisory: GHSA-qvpf-j64c-jmhr
CVE: CVE-2026-56835
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-qvpf-j64c-jmhr
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=3.11.0 <4.6.59

## Details
# PraisonAI Slack `app_mention` bypasses configured user/channel authorization

## Summary

PraisonAI's Slack bot applies its configured `allowed_users`,
`allowed_channels`, and unknown-user pairing policy in the normal Slack
`message` event handler, but not in the adjacent Slack `app_mention` event
handler.

A Slack workspace user who can mention the bot in a channel where the Slack app
is present can trigger the configured PraisonAI agent even when:

- the sender is not in `BotConfig.allowed_users`;
- the channel is not in `BotConfig.allowed_channels`;
- `unknown_user_policy="deny"` is configured; and
- the same event content is correctly dropped by the normal `message` handler.

This is a sibling-handler guard-coverage issue. Slack documents
`app_mention` as a distinct event type rather than a `message.*` event, so
deployments subscribed to app mentions can route unauthorized sender input
around the guarded message path.

## Affected product

- Repository: `MervinPraison/PraisonAI`
- Package: `praisonai`
- Component: `src/praisonai/praisonai/bots/slack.py`
- Configuration component: `src/praisonai-agents/praisonaiagents/bots/config.py`

Confirmed affected:

```text
v3.11.0  7f37d754a72511a71f7eeaaa8e9f367a5dc45fd8
v3.11.14 44b800df0eddf32dd5242f47da7513e4a3159d76
v3.12.0  51f95ad904a6616b35caede1cd74026ec8f7152c
v4.4.5   9a3363c900fa3be3fce5483be7f6c1f418757ebb
v4.4.6   90b00f9a25ee5c7ccf4b6ab3152700e1881f262d
v4.4.12  7d0657632fc477673153ad116cecf692b454bfa3
v4.5.2   8ddbb4ee7152d3fa68fbaaf6e6c610ae03d938d3
v4.5.16  02a19776517cc76483fd58dcd6a5fdf8c2c45170
v4.5.28  16f93251766505a79f237a0f07f68a0ecb17e358
v4.5.112 bfe3d94bad6db92fc2927c2e3c081ae8303e209e
v4.5.128 b4e3a8a84ade44ac3dd9102b792cdb4311a95937
v4.6.10  4b1b17b963cbd0625e41394a30168c95b26429b2
v4.6.33  dfbb8d78ec7e8dc7118bc722ab1b2524bc98ddab
v4.6.34  e5928449f73f66cc8af1de61621aa974ab255133
v4.6.56  d3c4a2afadfbf3a3e172e460e607ba4efad263a6
v4.6.57  e90d92231853161ad931f3498da57651a9f8b528
v4.6.58  1ad58ca02975ff1398efeda694ea2ab78f20cf3e
```

Unaffected boundary control:

```text
v3.10.24 de1734c29a50af18cf8c69e1d1d90e0f8e391aae
```

`v3.10.24` does not contain `src/praisonai/praisonai/bots/slack.py`.

Suggested affected range: `praisonai >= 3.11.0, <= 4.6.58`.

## Root cause

The guarded `message` handler converts the Slack event into a `BotMessage`,
then applies channel and sender policy before any agent call:

```python
@self._app.event("message")
async def handle_message(event, say):
    if event.get("bot_id"):
        return

    bot_message = self._convert_event_to_message(event)
    bot_message._channel_type = "slack"
    self.fire_message_received(bot_message)

    if not self.config.is_channel_allowed(
        bot_message.channel.channel_id if bot_message.channel else ""
    ):
        return

    user_id = bot_message.sender.user_id if bot_message.sender else ""
    is_explicitly_allowed = (
        bool(self.config.allowed_users) and self.config.is_user_allowed(user_id)
    )
    if not is_explicitly_allowed:
        user_allowed = await UnknownUserHandler.handle(bot_message, self._bot_context)
        if not user_allowed:
            return
```

Only after these checks does `handle_message` call the session manager and
agent.

The adjacent `app_mention` handler strips the bot mention and directly invokes
the agent session. It never calls `is_channel_allowed()`,
`is_user_allowed()`, or `UnknownUserHandler.handle()`:

```python
@self._app.event("app_mention")
async def handle_mention(event, say):
    if event.get("bot_id"):
        return

    text = event.get("text", "")
    if self._bot_user:
        text = text.replace(f"<@{self._bot_user.user_id}>", "").strip()

    if self._agent:
        user_id = event.get("user", "unknown")
        response = await self._session.chat(
            self._agent, user_id, text,
            chat_id=str(event.get("channel", "")),
            thread_id=event.get("thread_ts", "") or "",
            message_id=event.get("ts", ""),
            account=self._config.get("account", "default"),
        )
```

Older affected releases use `self._agent.chat(text)` instead of
`self._session.chat(...)`, but have the same policy gap: `message` checks
`allowed_users` and `allowed_channels`; `app_mention` does not.

## Local-only PoV

Run from the harness checkout:

```fish
env PYTHONPATH="artifacts/repos/praisonai-v4.6.58/src/praisonai:artifacts/repos/praisonai-v4.6.58/src/praisonai-agents" \
  python3 submission-bundle/praisonai-prai-cand-017-slack-app-mention-authz-bypass/poc/pov_prai_cand_017_slack_app_mention_authz_bypass.py \
    --repo artifacts/repos/praisonai-v4.6.58 \
    --label v4.6.58
```

The PoV mocks Slack Bolt and Slack SDK in-process. It does not connect to
Slack, bind a network port, or require real tokens.

The PoV configures:

```python
BotConfig(
    allowed_users=["U_ALLOWED"],
    allowed_channels=["C_ALLOWED"],
    unknown_user_policy="deny",
    mention_required=True,
)
```

It then invokes the real registered SlackBot handlers with the same event
payloads.

Observed `v4.6.58` result:

```json
{
  "affected": true,
  "scenarios": [
    {
      "name": "blocked_user_blocked_channel",
      "message_delta": 0,
      "app_mention_delta": 1
    },
    {
      "name": "blocked_user_allowed_channel",
      "message_delta": 0,
      "app_mention_delta": 1
    },
    {
      "name": "allowed_user_blocked_channel",
      "message_delta": 0,
      "app_mention_delta": 1
    },
    {
      "name": "allowed_user_allowed_channel_control",
      "message_delta": 1,
      "app_mention_delta": 1
    }
  ]
}
```

The first three scenarios are authorization bypasses. The fourth is the
positive control showing that an allowed user in an allowed channel can invoke
the agent through both paths.

Stored evidence:

- `evidence/pov-v4.6.58.json`
- `evidence/version-sweep.tsv`

## Why this is not intended behavior

PraisonAI's bot security documentation describes Slack user/channel allowlists
and built-in DM filtering as Slack security features. It also describes
`unknown_user_policy="deny"` and pairing flows as production controls for
unknown users.

The code itself confirms the intended boundary: the normal `message` handler
performs channel and sender authorization before any agent call. The vulnerable
`app_mention` path is adjacent to that handler and routes the same sender,
channel, text, timestamp, and thread metadata to the agent without those checks.

Slack's own documentation states that `app_mention` is a separate event type,
not a `message.*` event. A PraisonAI deployment that subscribes to
`app_mention` therefore cannot rely on the normal `message` handler to apply
the same sender/channel policy.

The PoV includes a direct control: the same unauthorized payloads are dropped
by the guarded `message` handler and accepted by `app_mention`.

## Impact

An attacker needs the ability to cause Slack to deliver an `app_mention` event
to the PraisonAI Slack app, such as by mentioning the bot in a channel where the
app is present or by using Slack's invite-by-mention flow where applicable.

When exploited, the attacker can submit arbitrary prompt text to the configured
PraisonAI agent despite Slack bot allowlists or pairing policy. The downstream
impact depends on the deployed agent and tools. PraisonAI's default bot config
auto-approves safe tools and includes web, memory, scheduling, file, planning,
and skill tools, so unauthorized invocation can affect confidentiality and
integrity in real deployments.

This report does not claim compromise of Slack itself, bypass of Slack request
signature verification, or arbitrary code execution by default.

## Suggested fix

Use one shared authorization preflight for every Slack ingress path before
firing message hooks or invoking agents.

Concrete patch direction:

1. Convert `app_mention` events through `_convert_event_to_message()` or a
   dedicated equivalent that preserves sender, channel, text, timestamp, and
   thread metadata.
2. Set `bot_message._channel_type = "slack"` for `app_mention`.
3. Run the same channel check, user allowlist check, and
   `UnknownUserHandler.handle(...)` policy used by `handle_message`.
4. Only then strip the bot mention and invoke `_session.chat(...)`.
5. Add regression tests for:
   - blocked user plus blocked channel: `message` and `app_mention` both drop;
   - blocked user in allowed channel: both drop;
   - allowed user in blocked channel: both drop;
   - allowed user in allowed channel: both invoke;
   - `unknown_user_policy="pair"`: `app_mention` starts the same pairing flow
     instead of invoking the agent.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-qvpf-j64c-jmhr
- https://github.com/MervinPraison/PraisonAI
