### Title
Webhook shop/topic identity spoofing via unsigned headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw request **body only**, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to attribute and route the webhook event are taken from **HTTP headers that are never covered by the HMAC signature**. This breaks the identity binding `hmac_signed_bytes == bytes_acted_upon`: the signature authenticates the payload but not the tenant/topic metadata that the app trusts to route and process it.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from headers, independent of the signed content: [2](#0-1) 

`HmacValidator.validate` only compares the HMAC against `verifiable_query.to_signable_string` (i.e. the body), never the headers: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts the unauthenticated header-derived `request.shop` and `request.topic` to build `WebhookMetadata` handed to the app's handler: [4](#0-3) 

Because the signature covers only the body, an unprivileged internet user who can obtain **any** one valid `(body, hmac)` pair — trivially achievable by installing the target app on their own store (a self-service, unprivileged action) and triggering a webhook with attacker-chosen body content (e.g. creating an order with attacker-controlled fields) — can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for any other known shop domain. The HMAC check still passes (it only validates the body), but the app's webhook handler receives `WebhookMetadata` attributing attacker-controlled data to a victim tenant.

### Impact Explanation
Apps commonly use the `shop` value from `WebhookMetadata` to select the tenant context (e.g., look up that shop's session/access token, write to that shop's records, or trigger tenant-scoped side effects). Since `shop` is not bound to the HMAC, an attacker can inject a webhook event with a body they fully control and route it to any target shop identifier, achieving cross-tenant data injection/confusion — a Critical-class impact (cross-tenant access) per the defined severity criteria, without needing `api_secret_key`, a token, or any privileged access.

### Likelihood Explanation
Likelihood is realistic: obtaining one legitimate `(body, hmac)` pair only requires the attacker to install the app on their own (attacker-controlled) shop — a normal, unprivileged flow for most public apps — and craft webhook-triggering data (e.g. order/product content) of their choosing. Replaying the captured body+HMAC to the public webhook endpoint with a modified `shop-domain` header requires no cryptographic knowledge, only header substitution.

### Recommendation
Bind the tenant/topic identity to the signature: include `shop`, `topic`, `webhook_id`, and `api_version` header values in the signed material verified by `HmacValidator`, or independently verify that the `shop` domain in the request corresponds to a shop the app actually has an active installation/session for before acting on the webhook.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g. `orders/create`) with attacker-chosen JSON body content; capture the raw body and the resulting valid `x-shopify-hmac-sha256` value from Shopify's real delivery.
3. Send a new POST request directly to the app's public webhook endpoint containing the identical captured body and `hmac-sha256` header, but with `x-shopify-shop-domain` set to `victim-shop.myshopify.com` (and, if desired, a different `x-shopify-topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because it only checks the body against the HMAC; `ShopifyAPI::Webhooks::Registry.process` proceeds to call the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled data>, ...)`, causing the app to process attacker-controlled data under the victim tenant's identity.

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
