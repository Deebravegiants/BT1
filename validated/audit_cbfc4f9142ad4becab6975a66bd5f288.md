I have sufficient evidence to confirm this finding.

### Title
Webhook shop domain identity spoofing due to `Shop-Domain` header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating that the HMAC in the `X-Shopify-Hmac-Sha256` header matches an HMAC of the raw request body, computed with the app's shared `client_secret`. The tenant-identifying `shop` field (and `topic`/`webhook_id`) is read straight from unauthenticated HTTP headers and is never included in the signed payload, so any request bearing a *previously valid* `(raw_body, hmac)` pair can be replayed with an arbitrary `X-Shopify-Shop-Domain` header and will still pass verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are never part of the signed string: [2](#0-1) 

`Registry.process` verifies only this body-only HMAC before dispatching the handler with the unauthenticated `shop` value: [3](#0-2) 

`HmacValidator.validate` computes and compares `HMAC(secret, to_signable_string)`, i.e. `HMAC(secret, raw_body)`, completely independent of `shop`: [4](#0-3) 

The resulting `WebhookMetadata` struct — which the host application uses to look up the tenant/session and act on the payload — carries this unauthenticated `shop` value straight through: [5](#0-4) 

**Identity binding broken:** the gem implicitly asserts `hmac_valid(raw_body) == shop_is_authentic`, but the actual invariant enforced is only `HMAC(secret, raw_body) == received_hmac`; `shop` is disjoint from that equality. Since `client_secret` is a single shared value across every merchant that installs the app (not per-tenant), any merchant who legitimately receives one valid `(raw_body, hmac)` webhook pair for their own shop can capture it and re-POST it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a different, victim merchant's domain. `HmacValidator.validate` still returns `true` because it never looked at the shop header, and `Registry.process` hands the forged shop identity straight to the handler.

### Impact Explanation
This is a cross-tenant boundary violation (Critical per the given scale): a low-privilege attacker (any merchant who has installed the app, i.e. an "unprivileged internet user" relative to other tenants) can make the host application process attacker-controlled webhook bodies as if they originated from an arbitrary victim shop, spoofing `shop` in `WebhookMetadata`. Any host application logic that trusts `WebhookMetadata#shop` to select which merchant's session/data to update (a documented and expected usage pattern for this gem) can be tricked into acting on the wrong tenant — e.g. injecting fake `orders/create`, `app/uninstalled`, `customers/data_request` or GDPR-topic events attributed to a different store, or triggering shop-specific cleanup/redaction logic for a store the attacker doesn't own.

### Likelihood Explanation
Any app merchant can trivially capture a valid `(raw_body, hmac)` pair for their own installation (webhooks are delivered to a URL the merchant/app developer controls) and replay it against the shared webhook endpoint with a forged `Shop-Domain` header — no access to `client_secret`, access tokens, or the victim's credentials is required. This is a low-effort, high-confidence attack path once an attacker has any single legitimate webhook delivery of their own.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material that `HmacValidator` verifies, or otherwise cryptographically tie the header-derived identity to the signed body (e.g., include the shop domain in the canonical string that is HMAC'd, matching the approach already used for `Auth::Oauth::AuthQuery#to_signable_string`, which folds `shop` into the signable string). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be independently cross-checked by the host application against a known/expected shop before use.

### Proof of Concept
1. App merchant A installs the app; Shopify delivers a legitimate webhook to the app's endpoint with body `B` and headers including `X-Shopify-Hmac-Sha256: H` (valid for `HMAC(secret, B)`) and `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
2. Attacker (merchant A) captures `(B, H)`.
3. Attacker POSTs the identical `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, B)` and compares to `H` — matches, returns `true` (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic:, shop: "shop-victim.myshopify.com", body:, ...))` (`lib/shopify_api/webhooks/registry.rb:198-199`), and the host application processes the forged payload believing it is authentic data for `shop-victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
