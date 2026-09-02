### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant identity spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` field that is subsequently trusted and handed to the application's handler is taken from an HTTP header that is never part of the signed data. This breaks the intended binding `hmac == HMAC(secret, body)` should also imply `shop == authenticated_shop`, mirroring the reported class of bug where an "insufficient" first-depositor mitigation let an attacker manipulate a value (`balance_of`) that was never actually protected by the accounting the code relied on.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, independent of the signature: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers the body) and then immediately trusts `request.shop` to build the `WebhookMetadata` that is delivered to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` confirms only that `hmac == HMAC(secret, verifiable_query.to_signable_string)`, i.e. it authenticates the body, not the shop header: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no indication to consuming code that it is unauthenticated: [5](#0-4) 

**Binding that should hold:** `hmac_valid(body) ⇒ shop_header == shop_that_generated(body)`.
**Binding that actually holds:** `hmac_valid(body) ⇒ body_was_signed_with_secret`, with **no constraint on the `shop` header at all**.

Because Shopify signs webhook payloads with the app's single `api_secret_key` shared across every shop that has the app installed, any body+HMAC pair that was legitimately generated for one shop (e.g., by an attacker who is a normal, unprivileged merchant that installed the app on their own store and triggered a webhook such as `orders/create`) remains a **valid** HMAC no matter which `shop-domain` header accompanies it. An attacker can therefore:
1. Capture a legitimately-signed `(raw_body, hmac)` pair generated from their own shop's activity (they need no `api_secret_key`, access token, or privileged role — just being a normal user of a store where the app is installed).
2. Replay it directly to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop.
3. `Registry.process` validates the HMAC successfully (it only checks the body) and dispatches `WebhookMetadata` with `shop` set to the victim's domain and `body` set to attacker-controlled content, to the app's handler.

### Impact Explanation
This crosses a tenant boundary: attacker-controlled webhook data is delivered to the application labeled as belonging to a different, victim shop, with a cryptographically "verified" wrapper. Any host application that (reasonably, given the gem's API) treats `WebhookMetadata#shop` as an authenticated tenant identifier — e.g., to look up/update per-shop state, inject records, or select credentials — can be made to act on forged data attributed to another tenant. This matches the Critical "cross-tenant access" impact category, since the gem's own primary/only authentication primitive for webhooks (`HmacValidator`) does not bind the field the application is expected to trust.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker needs at least one legitimately-signed `(body, hmac)` pair, which is obtainable by any ordinary/unprivileged party who can trigger a webhook from a shop where the target app is installed (e.g., a free trial or dev store, or their own merchant account), then simply resending it with a modified HTTP header outside of Shopify's servers to the app's public webhook URL. No `api_secret_key`, access token, or account privilege is required — only knowledge of the app's webhook endpoint and one captured legitimate delivery.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed payload verification, or otherwise cryptographically bind the `shop` value to the specific delivery instead of trusting the unauthenticated header. At minimum, `WebhookMetadata` and the library's documentation should explicitly flag that `shop` is not covered by the HMAC and instruct consumers to independently corroborate it against a source of truth (e.g., an installed-shop registry) before using it as a tenant key.

### Proof of Concept
```ruby
# Attacker triggers a legitimate webhook from their own installed shop,
# capturing the exact raw body Shopify sent and its valid HMAC header:
captured_body = '{"id": 1, "note": "hello from attacker shop"}'
captured_hmac = "<value Shopify computed with the app's shared api_secret_key>"

# Attacker replays it directly to the app's public webhook endpoint,
# forging the shop-domain header to point at the victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,     # still valid: HMAC only covers body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (body-only check),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: captured_body, ...))
# The app's handler now processes attacker-controlled data under the victim's identity.
``` [3](#0-2) [6](#0-5)

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
