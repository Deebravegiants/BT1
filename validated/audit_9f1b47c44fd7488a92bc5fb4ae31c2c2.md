## Finding

### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant/topic routing but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values used to route and attribute the webhook to a tenant are taken from unauthenticated HTTP headers that are never included in the HMAC computation. Anyone who can obtain one genuine `(raw_body, hmac)` pair (e.g., by installing the app on their own shop and triggering any webhook) can replay that exact body/HMAC pair while swapping the `shop-domain` header to a victim shop, and the library will report it as a validly-authenticated webhook for the victim shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` value: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw JSON body: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are not part of the signable string at all: [3](#0-2) 

`Registry.process` performs exactly one authentication check - the HMAC over the body - and then unconditionally trusts the header-derived `shop` (and `topic`) to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The equality the library implicitly claims to hold is:
`HMAC_valid(raw_body) == true` implies `shop-domain header == the shop that actually generated raw_body`.

That equality is false: the HMAC binds only the body bytes to the secret; it says nothing about which shop the header claims to be. An unprivileged internet user who runs (or installs) the app on their own shop can capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair for any webhook topic, then submit that exact pair to the app's public webhook endpoint with an attacker-chosen `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a different, victim shop. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is genuine), so `Registry.process` will invoke the registered handler believing the event originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook-authentication mechanism is supposed to provide: `HMAC valid ⇒ trust the accompanying shop/topic metadata`. Any host application that relies on `WebhookMetadata#shop` (as documented/intended, see `Registry.process`'s construction of `WebhookMetadata.new(topic:, shop:, body:, ...)`) to attribute events to the correct merchant - e.g., updating billing/subscription state, revoking data, writing merchant-scoped records, or triggering `app/uninstalled` cleanup - can be tricked into acting on behalf of, or against, a shop the attacker does not control. This is a cross-tenant identity-confusion vector rooted entirely in the gem's own `Request`/`Registry` code, not merely a misuse of an undocumented API: the gem exposes `request.shop` and `request.topic` as trusted, HMAC-validated fields, when in fact they are not bound to the signature at all.

### Likelihood Explanation
Exploitation requires no privileged credentials, no `api_secret_key`, and no access token: an attacker only needs to be a normal merchant who installs the (presumably public) app to legitimately trigger any webhook once and capture the resulting body + `hmac-sha256` header from their own shop, then replay it with a forged `shop-domain` header. This is a low-effort, remotely reachable attack against the gem's documented `Registry.process` entry point.

### Recommendation
Bind the tenant/topic identity to the HMAC-covered signable string, or otherwise authenticate the `shop-domain`/`topic` headers before trusting them, e.g.:
- Include the shop domain (and topic) in the value that is HMAC-verified, or
- Require the caller to independently corroborate `request.shop` against a known/installed shop record before invoking handlers, and reject webhooks whose header-derived shop cannot be corroborated.
At minimum, document that `Request#shop`/`#topic` are unauthenticated headers so implementers do not treat them as HMAC-verified.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker-shop.myshopify.com`) and triggers any webhook topic (e.g. `orders/create`), capturing the exact `raw_body` and the `x-shopify-hmac-sha256` header value Shopify sent - both are cryptographically valid because they were genuinely produced with the app's real `api_secret_key`.
2. Attacker POSTs the same `raw_body` to the app's public webhook endpoint again, but replaces the header:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <captured valid hmac>
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers/body (no cross-check between header and body).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-computes the HMAC over `raw_body` and succeeds (since the body/hmac pair is genuinely valid).
5. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's own order data>, ...)`, causing the host application to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

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
