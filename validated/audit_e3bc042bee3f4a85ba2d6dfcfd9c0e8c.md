### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` derives the tenant (`shop`) for a webhook exclusively from an HTTP header that is **not** covered by the webhook's HMAC signature, while the HMAC signature only authenticates the raw JSON body. Anyone who can obtain one valid `(body, hmac)` pair for their own shop (which any merchant legitimately receives) can replay it to the app's public webhook endpoint with an attacker-chosen `shop-domain` header and still pass HMAC validation, causing the app to process attacker-controlled data under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are computed only from `@raw_body`: [1](#0-0) [2](#0-1) 

`shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which plays no part in the signable string: [3](#0-2) 

`Utils::HmacValidator.validate` verifies only the bytes returned by `to_signable_string` against the `hmac` value, so it never binds the `shop` header to the signature: [4](#0-3) 

`Registry.process` trusts the HMAC check and then forwards the unauthenticated `request.shop` straight to the app's handler as the tenant identity: [5](#0-4) 

The equality the gem implicitly assumes but does not enforce is:
`shop_authenticated_by_hmac == shop_acted_on_by_handler`

In reality, `shop_authenticated_by_hmac` is undefined (HMAC covers only `body`), while `shop_acted_on_by_handler = header["shop-domain"]`, an attacker-controllable field once a valid `(body, hmac)` pair for *any* shop is known.

### Impact Explanation
Any user who can install the app on a shop they control (or otherwise obtain one legitimately-signed webhook delivery, e.g. from their own store) can capture a valid `(raw_body, hmac)` pair. They can then send the exact same body/HMAC to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. `HmacValidator.validate` still returns `true` because it never reads the header, and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"`. Any app that uses the `shop` value from `WebhookMetadata` to select which tenant's records to create/update/delete (the intended and documented use of this field) can be made to write attacker-controlled data into another merchant's tenant — a cross-tenant write, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining one valid signed webhook is trivial for any app user (install the app on a store you control, trigger any webhook topic that's registered), and replaying an HTTP POST with a modified header requires no cryptographic secret. No `api_secret_key`, access token, or privileged account is needed — this is achievable by any unprivileged internet user who can install the target app.

### Recommendation
Include the shop domain (and ideally the topic) inside the HMAC-signed material, or otherwise cryptographically bind the `shop-domain` header to the payload before trusting it. At minimum, `Utils::VerifiableQuery`/`HmacValidator` should be extended so `Webhooks::Request#to_signable_string` incorporates the shop and topic headers, and `Registry.process` should reject any HMAC computed over a mismatched shop/topic combination.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), legitimately receiving a POST with a valid `x-shopify-hmac-sha256` header computed over the JSON body and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the identical POST (same body, same `hmac` header) to the app's public webhook endpoint but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes the HMAC from `request.to_signable_string` (`@raw_body`, unchanged) and it matches the unchanged `hmac` header, so validation passes: [6](#0-5) 
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic:, shop: request.shop, body: request.parsed_body, ...))` with `shop` = `"victim-shop.myshopify.com"`, so the attacker's body is processed under the victim shop's identity: [7](#0-6)

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
