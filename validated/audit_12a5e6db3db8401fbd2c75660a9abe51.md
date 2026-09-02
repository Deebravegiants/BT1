### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` are read from unauthenticated HTTP headers. `Registry.process` validates only the body HMAC and then trusts these header-derived values as if they had been verified, breaking the binding `verified(hmac) == (body, shop, topic)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the request via `Utils::HmacValidator.validate(request)`, which only re-computes `HMAC(secret, to_signable_string)` i.e. `HMAC(secret, raw_body)`, and compares it to the header-supplied `hmac`: [3](#0-2) [4](#0-3) 

Once this passes, `Registry.process` dispatches to the handler with `request.shop` and `request.topic` treated as authenticated identity fields — but neither was included in the signed bytes. The equality the code implicitly assumes is:

`verified(hmac, raw_body) == (raw_body is genuine) AND (shop, topic, webhook_id are genuine)`

but the actual guarantee provided by the signature is only:

`verified(hmac, raw_body) == (raw_body is genuine, for *some* previously-signed webhook)`

An attacker who legitimately installs the app on their own store (fully unprivileged, no special credentials needed) will receive a validly-signed webhook `(raw_body, hmac)` for their own shop. Because `hmac` only binds to `raw_body`, that exact `(raw_body, hmac)` pair remains valid under `HmacValidator.validate` no matter what `shop-domain`/`topic`/`webhook-id` headers are attached to the replayed request. The attacker can therefore submit a request to the app's webhook endpoint with the original valid `(raw_body, hmac)` but with `x-shopify-shop-domain` set to a victim shop and/or `x-shopify-topic` set to a different registered topic, and the library will report it as a validated webhook for the victim shop/topic.

### Impact Explanation
This breaks the shop-identity binding that host applications rely on for tenant isolation and topic-based dispatch: `Registry.process` hands `request.shop` (attacker-controlled, unauthenticated) to the handler as the tenant identifier and `request.topic` as the event type, despite only the body having been cryptographically verified. A host app that scopes side effects (data mutation, redaction, uninstall handling, etc.) by `WebhookMetadata#shop` can be made to perform actions attributed to, or affecting, a different merchant's tenant using content the attacker fully controls (their own genuine webhook body) — a cross-tenant confusion caused entirely by this gem's own `Registry.process`/`Request` implementation, not by host misuse.

### Likelihood Explanation
Any developer with access to the same app's webhook secret indirectly (by installing the app as a normal, unprivileged merchant) can obtain a valid `(raw_body, hmac)` pair for their own shop without needing `api_secret_key`, an access token, or any privileged access — satisfying the "unprivileged internet user" bar. Crafting the replay request with modified headers is trivial (a normal HTTP POST), so the likelihood of exploitation is high wherever a host relies on `Registry.process`'s HMAC check as proof of shop/topic authenticity.

### Recommendation
Include the shop domain, topic, and/or webhook id in the HMAC-signed material (or otherwise cryptographically bind them), for example by having `Request#to_signable_string` incorporate the header values that `Registry.process` later trusts, or by requiring the caller to separately verify `shop`/`topic` against context that is out of the attacker's control (e.g., matching an active, previously-established session/tenant), before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends a POST to the app's webhook endpoint with the same body `B` and same `hmac` header `H`, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or changes `x-shopify-topic` to another registered topic).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [1](#0-0)  and finds it matches `H`, so validation succeeds.
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked [5](#0-4)  with `shop` = `victim-shop.myshopify.com`, even though the signature never covered that value — demonstrating the header/HMAC identity-binding break.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
