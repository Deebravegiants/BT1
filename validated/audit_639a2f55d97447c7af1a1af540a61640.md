### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-spoofing / cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw JSON body, then trusts the `shop-domain` header — which is never included in the signed material — as the tenant identifier passed to the app's handler.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then immediately forwards `request.shop` to the app's handler as the authoritative tenant identity: [3](#0-2) 

The binding that should hold is:
`hmac_valid(body) == true` **should imply** `shop == the shop that Shopify actually generated this signed body for`.

In reality the equality that holds is only `hmac_valid(body) == true` **for that specific body**, independent of any `shop` value — the `shop` header is bytes that are *parsed* and handed to the handler, but never *verified* as bound to the signed bytes. This is the same class of defect as the reported bug: a field that is acted upon (here, tenant/shop identity) is not covered by the cryptographic check that gates trust (here, the webhook HMAC), exactly analogous to `globalTotalStaked` being read before the frozen-token state it depends on was updated — the value used for a security decision is stale/unbound relative to what was actually verified.

### Impact Explanation
Any internet user who can trigger a legitimately-signed webhook for *some* shop (e.g., their own free/dev store on which the target app is installed) obtains a valid `(raw_body, hmac)` pair signed with the app's `client_secret`. Because the `shop-domain` header is outside the signed content, that same body/HMAC pair can be replayed to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to an arbitrary victim shop domain. `Utils::HmacValidator.validate` will still return `true` (it only recomputes the HMAC over the body), and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` claims to be the victim tenant while the `body` is actually the attacker's own data: [4](#0-3) [5](#0-4) 

Any host application that follows the gem's documented pattern of trusting `WebhookMetadata#shop` for tenant-scoped writes (installing/uninstalling records, updating per-shop settings, billing state, order/inventory sync, etc.) can be made to attribute attacker-controlled data to a different merchant's tenant record — a cross-tenant integrity/confusion issue.

### Likelihood Explanation
Requires only an internet-reachable webhook endpoint and the ability to obtain one genuinely-signed webhook (trivial: install the target app on any store, including the attacker's own, and capture the delivered request). No access token, `client_secret`, or privileged account is needed — the attacker never needs to know the secret, only to replay body+HMAC bytes they already legitimately received with a rewritten header.

### Recommendation
Bind the shop identity into the HMAC verification, e.g. include `shop-domain` (and `topic`) in the signable string, or independently confirm the `shop-domain` header against a value already associated with the delivered `webhook_id`/topic registration before exposing it via `WebhookMetadata`. At minimum, document prominently that `Request#shop` is unauthenticated header data and must not be used as the sole tenant key without additional server-side correlation (e.g., checking against the shop associated with the webhook subscription id via the Admin API).

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the raw request: body `B`, and header `shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), plus `shopify-shop-domain: attacker.myshopify.com`.
2. Replay the identical `B` and `H` to the app's webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `B` only and returns `true`: [6](#0-5) 
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker's parsed body>, ...)`, causing the app to process attacker-controlled data under the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
