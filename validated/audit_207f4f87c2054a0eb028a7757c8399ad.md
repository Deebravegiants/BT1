## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (from the `x-shopify-shop-domain`/`shopify-shop-domain` header) is read and trusted separately, without being part of the signed material. `ShopifyAPI::Webhooks::Registry.process` validates only the body-derived HMAC and then hands the header-derived `shop` straight to the app's webhook handler. Because the `api_secret_key` used to compute the HMAC is shared across all shops that install the same app, any merchant who legitimately receives a validly-signed webhook can replay that same body/HMAC pair while swapping the `shop-domain` header to a victim shop's domain, and the signature will still validate.

### Finding Description
The identity binding that should hold is: `shop attributed to a webhook == shop whose body/HMAC pair authenticates it`. In this gem that binding is broken because the HMAC only binds the body: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`; the `shop` header is exposed via a separate accessor that reads directly from headers, uncovered by the signature: [3](#0-2) 

`Utils::HmacValidator.validate` verifies exactly this signable string against the app's `api_secret_key`: [4](#0-3) 

`Registry.process` checks only this HMAC, then forwards the *header-derived* `shop` (along with the verified body) to the handler as trusted `WebhookMetadata`: [5](#0-4) 

Since `api_secret_key` is per-app, not per-shop, any two shops that install the same app share the same HMAC key. A merchant/attacker who operates their own store with the app installed can capture a legitimate webhook delivery (raw body + valid `hmac-sha256` header) sent to their own endpoint, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header value. `HmacValidator.validate` will still succeed, because the header is never part of `to_signable_string`, and the handler will process the replayed body as if it genuinely originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem's own webhook verification is supposed to establish: the whole purpose of `Registry.process`/`HmacValidator` is to let an app trust `data.shop` when routing/handling webhook payloads. Because `shop` is unauthenticated with respect to the signature, an attacker with a legitimate (even free/trial) app install can inject attacker-controlled webhook data attributed to any other shop using the app, without needing that victim's credentials, access token, or `api_secret_key`. Depending on the handler logic (e.g. handlers that key data storage, entitlements, or side effects off `data.shop`), this is a cross-tenant data/state injection into another merchant's context — a Critical-class cross-tenant access impact, since it lets one unprivileged tenant impersonate another tenant purely by header manipulation on an otherwise-valid signed payload.

### Likelihood Explanation
Likelihood is high for any app that: (a) allows any merchant to install it (even attacker-controlled test/free shops), and (b) exposes a `Registry`-based webhook endpoint. No secret material, TLS interception, or social engineering is required — only the ability to receive one legitimate webhook to your own store (trivial, e.g. by triggering an `orders/create` in your own dev store) and replay it with a modified header to the shared endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise verify that the shop claimed in the header actually installed the app / is authorized for the topic before trusting `data.shop`. Concretely:
- Include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (this requires coordinating with Shopify's webhook delivery format, which currently signs body only) — or,
- At the application layer (and as a gem-level safeguard), cross-check the `shop` header against a known/authorized shop list (e.g. the app's installed-shop store) before invoking the handler, rejecting webhooks for shops that are not recognized as legitimately installed, rather than trusting the header purely because the body-only HMAC validated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g. `orders/create`), capturing the raw request: body `B`, and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Attacker crafts a new HTTP request to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`, which calls `Utils::HmacValidator.validate(request)`:
   - `request.to_signable_string` returns `B` (header-independent) — signature check passes.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, i.e., attacker-controlled data is processed as though it belongs to `victim-shop.myshopify.com`. [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
