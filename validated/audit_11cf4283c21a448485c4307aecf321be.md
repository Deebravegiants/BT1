### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `api_version`, `webhook_id`) that gets passed to the application's webhook handler from unauthenticated HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies only covers the raw request body. This breaks the identity binding `shop verified by HMAC == shop acted upon by the handler`.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the body that was actually signed: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the signature over `to_signable_string` (the raw body) and compares it against the `hmac` field — it never incorporates the `shop`, `topic`, `webhook_id`, or `api_version` headers into the signed material: [3](#0-2) 

`Webhooks::Registry.process` then trusts `request.shop` (from the unauthenticated header) to identify the tenant when invoking the handler: [4](#0-3) 

Because the HMAC only authenticates the body bytes and not the header set, any party who can obtain one genuinely-signed webhook body/HMAC pair (e.g., by installing the app on their own store and receiving a legitimate webhook for their own shop) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still succeed (the body and secret haven't changed), but `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to a different, attacker-chosen shop — `data.shop` set from the forged header value.

### Impact Explanation
This breaks the binding "shop verified by HMAC == shop the data is attributed to," which is exactly the class of identity-binding bug called out in scope (a field acted on but not covered by the HMAC). Host applications built on this gem rely on `WebhookMetadata#shop` to route/attribute incoming webhook data per tenant; an attacker can make legitimately-signed data appear to originate from an arbitrary victim shop domain, which is a cross-tenant data integrity/confusion issue reachable by any unprivileged party who can install the app on a store they control (no access token, `client_secret`, or privileged account needed beyond that).

### Likelihood Explanation
Likelihood is high for any app that (a) allows installs by arbitrary merchants (the normal Shopify app model) and (b) uses `request.shop`/`data.shop` to key persistence or business logic, since replaying a captured, validly-signed webhook body with a modified shop header is trivial once an attacker has any legitimate webhook of their own to capture.

### Recommendation
Bind the shop (and topic/webhook id) into the signed material, or otherwise cryptographically tie the header-derived `shop` to the verified payload — e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or validate `shop` against the shop encoded inside the parsed webhook body where Shopify includes it, rather than trusting the header alone.

### Proof of Concept
1. Attacker creates a development store and installs the target app, causing Shopify to deliver a legitimately-signed webhook (e.g., `orders/create`) with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, body `B`.
2. Attacker replays the identical body `B` and `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only [5](#0-4)  — validation passes because `B` and the secret are unchanged.
4. `Registry.process` invokes the handler with `shop: request.shop` = `"victim-shop.myshopify.com"` [6](#0-5) , causing the host app to process/store attacker-controlled data under the victim's tenant identity.

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
