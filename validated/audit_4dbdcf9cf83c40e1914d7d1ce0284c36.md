### Title
`X-Shopify-Shop-Domain` header is trusted without HMAC binding, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the webhook HMAC signature over the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are taken from unauthenticated HTTP headers that are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body/HMAC pair validates and then blindly forwards `request.shop` to the app's webhook handler as the tenant identifier, breaking the intended binding between "bytes verified" and "bytes acted on."

### Finding Description
The signable content for a webhook request is defined as just the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from HTTP headers with no cryptographic tie to the HMAC: [2](#0-1) 

`HmacValidator.validate` only proves that `to_signable_string` (i.e., the raw body) was signed with `Context.api_secret_key`; it says nothing about the `shop-domain` header: [3](#0-2) 

`Registry.process` uses this unverified `request.shop` value directly to construct the metadata handed to the app's business logic: [4](#0-3) 

Because the api_secret_key is shared across every shop that installs the app (it is not shop-specific), an attacker who legitimately installs the app on their own shop receives real, validly-signed webhook deliveries (body + correct `X-Shopify-Hmac-Sha256`). Since the shop domain is never part of the signed content, the attacker can replay that same body/HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` with a victim shop's domain. `HmacValidator.validate` still succeeds (only the body is checked), and `Registry.process` dispatches the handler with `shop: <victim shop>`, so the equality the code implicitly relies on — "the shop that signed this payload" == "the shop the handler believes it is processing for" — is broken.

### Impact Explanation
This is a cross-tenant boundary violation: an unprivileged attacker who controls one legitimately-installed shop can forge webhook events that appear to originate from a different (victim) shop, because the shop identity is not bound to the HMAC. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to select which merchant's DB record/session to update, trigger side effects, or infer authorization), this enables cross-tenant data confusion/injection — matching the "cross-tenant access" critical impact category.

### Likelihood Explanation
Likelihood is high for any attacker who can install the app on at least one shop (a normal, unprivileged flow for public apps) and can also send arbitrary HTTP requests to the app's public webhook endpoint. No secret material beyond a legitimately-received webhook payload is required, and the header spoof is trivial.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed content, or otherwise cryptographically bind the header value to the verified payload (e.g., validate that the shop-domain header matches a shop identifier embedded in the signed body, or maintain a per-shop webhook secret/registration check) before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture a legitimate webhook delivery: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Send a forged HTTP POST to the app's webhook endpoint with the same body `B` and the same header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `HmacValidator.validate` returns `true` because it only checks `B` against `H`.
4. `Registry.process` invokes the registered handler with `shop: "victim.myshopify.com"`, even though the payload never originated from that shop — demonstrating the broken shop↔HMAC binding.

### Citations

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
