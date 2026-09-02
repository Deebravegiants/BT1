### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) fields are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values used to dispatch and populate `WebhookMetadata` are taken directly from unauthenticated HTTP headers that are never included in the signed payload. Since Shopify signs webhooks for a given app with the *same* `client_secret` regardless of which installed shop sent them, any shop that has legitimately installed the app can capture one of its own valid signed webhook deliveries and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, producing a request that passes HMAC validation but is attributed to the wrong tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from request headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, i.e. the raw body only: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authentication for the whole request, then builds `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`, and forwards it to the app's handler: [4](#0-3) 

The equality the gem implicitly claims to guarantee is:
`shop authenticated by HMAC == shop delivered to the handler`

In reality, because Shopify's webhook HMAC is computed only over the JSON body using the app's single `client_secret` (shared across every shop that installs the app), the signature is valid for the body regardless of which shop header accompanies it. An attacker who controls (or has installed the app on) shop A can capture a legitimate webhook delivery (body + valid HMAC) for shop A, then resend it to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to shop B. `HmacValidator.validate` still returns `true` because it only checks the body against the secret, and `Registry.process` dispatches the handler with `shop: "B"`, even though the payload never originated from Shopify for shop B.

### Impact Explanation
This breaks a tenant-isolation boundary in the webhook layer of the gem. Host applications rely on `WebhookMetadata#shop` (and `#topic`) as the authenticated identity of the sending shop to look up sessions, update per-shop records, or perform destructive/compliance actions — notably the mandatory topics `shop/redact`, `customers/redact`, `customers/data_request`: [5](#0-4) 

An attacker who is themselves an installed merchant of the app (an "unprivileged internet user" from the app's perspective, with no elevated credentials) can cause the app to process events attributed to a different shop, resulting in cross-tenant data confusion/manipulation without ever possessing the target shop's access token or the app's `client_secret`.

### Likelihood Explanation
Any user who can install the app on their own shop can obtain one valid (body, HMAC) pair from a real Shopify-delivered webhook and replay it with a forged `shop-domain` header to the app's public webhook endpoint. No secrets belonging to the victim shop or the app owner are required — only observation of the attacker's own webhook traffic, which is trivial to capture.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is cryptographically verified, or otherwise cross-check the header-derived `shop` against an independent trusted source before dispatching to the handler. Concretely:
- Include the `shop-domain` (and `topic`) header content in the signable string used by `HmacValidator`, mirroring Shopify's actual webhook verification guidance which recommends validating headers are consistent with the registered webhook subscription for that shop, or
- After HMAC validation, verify that a webhook subscription with the delivered `webhook_id`/`topic` is actually registered for the `shop` claimed in the header (e.g., by checking against the app's own registered webhook records for that shop) before invoking the handler, and
- Document clearly for consumers of `WebhookMetadata` that `shop` is not currently covered by the HMAC, so host apps are not misled into treating it as fully authenticated.

### Proof of Concept
1. App merchant "attacker-shop.myshopify.com" installs the vulnerable app and triggers any webhook topic (e.g. `orders/create`) on their own store, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify.
2. Attacker resends this exact body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and `X-Shopify-Topic` to a topic the app has registered for the victim (e.g. `customers/redact`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body`, and the check passes. [6](#0-5) 
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built using the attacker-controlled headers and passed to the app's `handler.handle`, which believes the event pertains to `victim-shop.myshopify.com`. [7](#0-6)

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
