Confirmed: the webhook `process` flow at [1](#0-0)  validates the HMAC against the raw body only and then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using `request.shop`, which is a plain header value never covered by the signature.

### Title
Webhook `shop` domain is trusted without being bound to the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](https://github.com/Tylerpinwa/shopify-api-ruby--017))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [2](#0-1) , so `Utils::HmacValidator.validate` only cryptographically binds the *body bytes* to the app's `api_secret_key`. The `shop` value, read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, is never part of the signed material [3](#0-2) . `Registry.process` validates the HMAC and then forwards `request.shop` straight into `WebhookMetadata`, which host apps use as the tenant identifier for all downstream processing [4](#0-3) .

### Finding Description
The equality that should hold is: `shop bound by HMAC == shop acted upon by the handler`. In this code it does not — `HmacValidator.validate_signature` computes `HMAC(api_secret_key, raw_body)` and compares it to the `hmac-sha256` header [5](#0-4) , while the `shop` field consumed by `Registry.process` comes from an entirely separate, unauthenticated header [3](#0-2) .

Any entity that can install the app on a shop it controls (a normal, unprivileged partner/merchant action) will receive genuine webhooks with a valid `hmac-sha256` for a given body. Because the signature never covers the `shop-domain` header, that same `(body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `shop-domain` header rewritten to any victim shop. `Utils::HmacValidator.validate` still returns `true` since it only re-derives the HMAC from the body [6](#0-5) , and the handler receives `shop: <attacker-chosen victim domain>` as if Shopify itself vouched for it.

### Impact Explanation
This breaks the tenant identity binding at the point where the library hands control back to the host application. Mandatory topics such as `shop/redact`, `customers/redact`, and `customers/data_request` [7](#0-6)  as well as ordinary topics like `app/uninstalled` or `orders/create` are dispatched using this unauthenticated `shop` value, so an attacker can make a host app believe an action (uninstall cleanup, data deletion, order ingestion, etc.) originated from a shop it never actually came from — a cross-tenant data/action injection into any app built on this gem's webhook handling.

### Likelihood Explanation
Exploitation only requires installing the app once on an attacker-controlled development/trial shop to obtain a valid `(body, hmac)` pair for a chosen topic, then re-POSTing it with a forged `shop-domain` header. No access to the app's `api_secret_key` or any victim credential is required, making this reachable by any unprivileged internet user who can install the target app.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signable material, or — since Shopify's wire format cannot be changed — have `Registry.process`/`WebhookMetadata` cross-check `request.shop` against a set of shops known to have valid sessions/installations for this app before dispatching, rather than trusting the header outright once the body HMAC passes.

### Proof of Concept
1. Install the target app on an attacker-owned shop `attacker.myshopify.com`; capture a legitimate webhook POST, e.g. topic `app/uninstalled`, with headers `x-shopify-hmac-sha256: <valid H>` and body `B`.
2. Replay the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are computed purely from `B` [8](#0-7) ; `HmacValidator.validate` succeeds because `HMAC(secret, B) == H` regardless of the header change [9](#0-8) .
4. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` [10](#0-9) , causing the host application to perform tenant-scoped actions against the victim shop's data on the attacker's behalf.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
