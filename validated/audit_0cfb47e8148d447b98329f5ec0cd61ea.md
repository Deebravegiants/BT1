### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is not covered by the HMAC signature, allowing cross-tenant webhook body replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity by HMAC-checking only the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that the app actually acts on are read from HTTP headers that are excluded from the signed material. Anyone who can obtain one valid `(raw_body, hmac)` pair for their own shop can replay that exact body to the same endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The signature still validates (it only ever covered the body), so the host application will process/store attacker-supplied but "verified" data under a victim shop's identity — a tenant-identity binding break.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed directly from unauthenticated headers with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string`, i.e. the body alone, using `Context.api_secret_key`: [3](#0-2) 

`Registry.process` gates only on this body HMAC, then immediately forwards the unverified `request.shop`, `request.topic`, and `request.webhook_id` to the app's handler as trusted metadata: [4](#0-3) 

The identity binding that should hold is: `shop header == shop that produced/authorizes this body`. Before the attacker's request: a legitimate webhook for shop A arrives with `raw_body_A` + `hmac(raw_body_A, secret)` + `shop-domain: A`. After the attacker's request: the attacker (who is a merchant/installer of the app on shop A, and therefore legitimately receives that exact webhook once) resends the identical `raw_body_A` and `hmac(raw_body_A, secret)` to the app's webhook endpoint, but with `shop-domain: B` (a victim shop). `HmacValidator.validate` still returns `true` because it only checks the body against the secret, which is unchanged. `Registry.process` then calls the app's handler with `shop: "B"` and the (fully valid-looking) body from shop A, causing the host application — following exactly the documented usage pattern shown in the gem's own docs (`data.shop`, `data.body` trusted together) — to process/store shop A's data as if it belonged to shop B.

### Impact Explanation
This is a cross-tenant data-confusion vector: an attacker who is a merchant of one shop (or otherwise obtains a single legitimate webhook body+HMAC, e.g. by installing a free/trial app) can inject that verified-looking payload into another tenant's data stream by only forging the routing header, without needing the app's `api_secret_key`, an access token, or any other credential belonging to the victim. Depending on what the host app does with `data.shop`/`data.body` (e.g., updating inventory records, order state, or triggering shop-scoped business logic), this can lead to cross-tenant data corruption or unauthorized state changes attributed to a shop the attacker does not control — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs at least one legitimate `(raw_body, hmac)` pair, which they can trivially obtain by installing the app on their own store and receiving any subscribed webhook (a normal, unprivileged action available to any developer/merchant using the app). From there, forging the header and replaying the request is straightforward with any HTTP client. No secret key, TLS interception, or social engineering is required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers, which is inherent to how the gem's webhook consumer is expected to work.

### Recommendation
Bind the routing headers to the signed content, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the verified payload before trusting them:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (`to_signable_string`) so header tampering invalidates the signature, or
- Require the host application to independently verify that the `shop` header corresponds to a shop with an active session/install before processing the body, and document this requirement prominently since `ShopifyAPI::Webhooks::WebhookHandler` implementers currently receive `shop` as if it were already verified.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and subscribes to a webhook topic (e.g. `orders/create`) via the app's normal flow.
2. Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid_hmac>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - Body: `{"id": 1, "note": "test"}`
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value.
4. Attacker sends a new POST request to the same webhook endpoint with the identical body and HMAC header, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only checks the (unchanged) body against the (unchanged) secret: [5](#0-4) 
6. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: {"id"=>1,"note"=>"test"}, ...)` and the host app processes/stores this as data belonging to `victim-shop.myshopify.com`, even though it never originated from that shop.

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
