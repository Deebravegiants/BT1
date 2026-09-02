Confirmed. The `Registry.process` method validates only `Utils::HmacValidator.validate(request)`, and `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `topic`, `shop`, `api_version`, and `webhook_id` are pulled straight from unauthenticated headers and forwarded to the handler as trusted values. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop` (and `topic`) identity not bound by HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic for a given shop and topic solely because `Utils::HmacValidator.validate(request)` returns `true`. However, the HMAC signable string used for verification is only the raw request body — it never covers the `shop`, `topic`, `webhook_id`, or `api_version` values that are read from HTTP headers and handed to the app's handler. Any party who can obtain one valid `(body, hmac)` pair signed with the app's `client_secret` (e.g., a legitimate merchant who installs the app on their own store and captures a real webhook delivery) can replay that exact body/HMAC pair directly to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The signature still validates because the HMAC never bound the shop identity, so the app's handler executes business logic believing the event came from a different, victim tenant.

### Finding Description
The intended identity binding is: `HMAC_valid(body, secret) == true` should imply the request authentically originates for the `shop`/`topic` claimed. In this gem that equality is broken.

- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

- Yet `shop`, `topic`, `api_version`, and `webhook_id` are all sourced from raw, attacker-controllable HTTP headers with no cryptographic tie to the signed body: [4](#0-3) 

- `Utils::HmacValidator.validate` computes and compares the signature only over `verifiable_query.to_signable_string`, i.e. the body: [5](#0-4) 

- `Registry.process` gates entirely on that body-only HMAC check and then constructs `WebhookMetadata` directly from the unauthenticated headers, passing `shop: request.shop` and `topic: request.topic` straight to the app's handler: [6](#0-5) 

Because a single `client_secret` is shared across every shop that has the app installed, any merchant who installs the app can trigger a genuine webhook to their own store, capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair (which is valid because it was really signed by Shopify with the app's secret), and then send that identical body+HMAC pair directly to the app's public webhook endpoint URL while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a different, victim shop. `HmacValidator.validate` will still return `true` (the body and HMAC match), and `Registry.process` will invoke the handler with `shop` set to the victim's domain and attacker-supplied body content, causing the host application to process attacker-controlled webhook data attributed to another tenant.

### Impact Explanation
This breaks the tenant-identity binding relied upon by any host application that uses the webhook `shop` (or `topic`) field to route processing to per-tenant records — a standard and documented pattern for consuming Shopify webhooks (e.g., updating/deleting a shop's data on `app/uninstalled`, `shop/redact`, `customers/redact`, etc.). An attacker with no more privilege than "installs the app on their own store" can inject attacker-controlled webhook payloads that the app believes originated from an arbitrary victim shop, i.e., cross-tenant data manipulation — satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple, mutually-untrusting shops (the normal Shopify app model): obtaining one genuine `(body, hmac)` pair only requires installing the app on an attacker-owned store and triggering any webhook whose body content the attacker can influence (or a webhook whose fixed content is enough for the target logic, e.g., `app/uninstalled` has an empty/minimal body). No access to `api_secret_key`, tokens, or the target shop is required — only a normal internet-reachable POST to the app's public webhook URL.

### Recommendation
Bind the shop/topic identity into the verified signature. At minimum, the gem should reject or clearly document that `request.shop`/`request.topic` are unauthenticated header values that must be independently correlated against the shop identity that legitimately owns the corresponding session/`webhook_id` before being trusted. Preferably, `Utils::HmacValidator`/`Webhooks::Request#to_signable_string` should also verify that the `shop-domain` header, once combined with `raw_body`, matches an expected value known to `Registry` (e.g. cross-check `webhook_id`/`shop` against Shopify's admin API, or require callers to independently confirm the shop is one that has previously completed OAuth) instead of trusting it purely because the body-only HMAC matched.

### Proof of Concept
1. Install the target app on an attacker-controlled development store `attacker.myshopify.com`.
2. Trigger a webhook subscribed by the app (e.g. `customers/create`) with attacker-chosen body content; capture the raw POST, including the `x-shopify-hmac-sha256` header and body — this HMAC is valid because Shopify signed it with the shared `client_secret`.
3. Replay the exact captured body and `x-shopify-hmac-sha256` value directly to the app's public webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com` (and adjust `x-shopify-topic`/`x-shopify-webhook-id` as desired).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
5. The registered handler executes with `data.shop == "victim.myshopify.com"` and attacker-controlled `data.body`, even though the request never touched Shopify's servers for that shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
