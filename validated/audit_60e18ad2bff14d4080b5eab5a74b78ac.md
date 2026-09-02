## Cross-Tenant Webhook Spoofing via Shop Field Not Covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook `Request` object's HMAC signable string only binds the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) fields are read directly from unauthenticated HTTP headers and are never included in the HMAC computation. `Registry.process` trusts `request.shop` as the tenant identifier once the HMAC on the body passes, breaking the binding `shop-covered-by-HMAC == shop-acted-on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all sourced from request headers, none of which are part of the signable string: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, so the header-derived `shop` value never enters the equality check: [3](#0-2) 

`Registry.process` verifies the HMAC over the body, then unconditionally dispatches to the topic handler using `request.shop` as the tenant identity: [4](#0-3) 

Because Shopify signs webhooks with the app's single shared `client_secret` (identical across every shop that installs the app), a valid `(raw_body, hmac)` pair captured from a webhook delivered to *any* shop that has installed the app — including a low-privilege attacker's own store — remains valid regardless of which `x-shopify-shop-domain` header value accompanies it. This is the same bug class as the referenced report: a field that gates tenant-scoped behavior (`derivative` enabled-state there, `shop` header here) is not covered by the check that is supposed to bind it (`totalWeight`/deposit-loop there, HMAC signature here).

### Impact Explanation
An attacker who has installed the app on their own (attacker-controlled) shop can trigger any webhook topic on their store to obtain a legitimately-signed `(raw_body, hmac)` pair, then replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim merchant's domain. `HmacValidator.validate` still succeeds because it never checked `shop`, and `Registry.process` hands the handler a `WebhookMetadata` claiming the victim shop as the source. Any host application logic that trusts `WebhookMetadata#shop` for tenant-scoped actions (e.g., looking up the victim's stored session/access token to act on their store, updating victim-shop records, billing, uninstall handling, etc.) is misled into cross-tenant execution — this satisfies the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker be able to install the app on a shop they control (a standard, low-privilege step available to any unprivileged internet user with a development/trial shop) and send a raw HTTP POST to the app's public webhook endpoint with a forged header — no access token, `client_secret`, or privileged account is needed. This is fully within the "unprivileged internet user" threat model specified.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signable string used for HMAC verification, or otherwise cryptographically bind the header-derived tenant identity to the signed payload, so that `HmacValidator.validate` fails whenever the `shop` header does not match the shop the body was actually signed for.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic, capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header `H` (valid because it was computed with the app's shared `client_secret`).
2. Attacker sends a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the forged header [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [6](#0-5) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload originated from the attacker's shop, causing any tenant-scoped processing to run against the victim's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
