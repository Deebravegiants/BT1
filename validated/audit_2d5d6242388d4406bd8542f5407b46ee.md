### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from unauthenticated HTTP headers, while the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. This breaks the identity binding between "the shop that the HMAC authenticates" and "the shop the handler acts on," allowing a party who can obtain one valid `(raw_body, hmac)` pair to relabel it as coming from any other shop or topic.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers that are never mixed into the signable string: [2](#0-1) 

`Registry.process` only validates the HMAC over the body, then passes the header-derived `shop`/`topic`/`webhook_id` straight to the app's handler as trusted metadata: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. the body, via `compute_signature`: [4](#0-3) 

The identity binding broken here is: `shop covered by HMAC` (∅, since HMAC only signs body bytes) vs. `shop delivered to the webhook handler as the tenant key` (`request.shop`, taken from the `shopify-shop-domain`/`x-shopify-shop-domain` header). These two are not equal, yet the gem treats a successful HMAC check on the body as implicit authentication of the header-derived shop and topic.

### Impact Explanation
Because the shop/topic/webhook_id headers ride outside the signed payload, any party who legitimately receives one valid webhook delivery (e.g., an attacker who installs the same app on their own shop and captures a real `(raw_body, hmac)` pair for a topic they control) can replay that exact body+hmac to the app's shared webhook endpoint while substituting the `shopify-shop-domain` header for a victim merchant's domain. `Registry.process` will pass HMAC validation (since the body is unchanged) and invoke the handler with `WebhookMetadata` claiming the victim shop, causing the app to process attacker-controlled webhook data under another tenant's identity — a cross-tenant confusion in the trust the gem provides to host applications for tenant attribution.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one genuine `(raw_body, hmac)` pair, which is achievable by installing the app on a shop they control (a normal, unprivileged action available to any developer/merchant) and capturing their own webhook deliveries. No access to `api_secret_key` or any victim credentials is required — only manipulation of unauthenticated headers on the replayed HTTP request.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, and ideally `webhook_id`) into the HMAC-signable representation, or otherwise cryptographically tie them to the payload, so that `HmacValidator.validate` fails if any of these fields are altered independently of the signed body. At minimum, document to host applications that `request.shop`/`request.topic` are not authenticated by the HMAC check and must be independently cross-checked against the session/tenant the webhook is expected for.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` computed by Shopify over `B`.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds despite the mismatched shop header. [5](#0-4) 
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to act as if the (attacker-controlled) payload originated from the victim shop.

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
