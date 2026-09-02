### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body when validating a webhook's HMAC, but the `shop` (i.e., `shop-domain` header) and `topic`/`webhook_id` values used to route and attribute the webhook to a specific merchant are read directly from unauthenticated HTTP headers and are never included in the signed payload. This breaks the identity binding: `hmac_valid(raw_body) == true` is treated as proof that `shop-domain header == originating shop`, when in fact the two are independent.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature only over `to_signable_string` (i.e., the raw body) using the app's `client_secret`: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then trusts the unauthenticated `request.shop` header when constructing `WebhookMetadata` passed to the host app's handler: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is a single app-level secret shared across every shop that installs the app — not a per-shop secret — a valid `(raw_body, hmac)` pair generated for one shop's webhook remains valid regardless of which `shop-domain` header accompanies it. Any party who can capture a legitimately-delivered `(raw_body, hmac)` pair (e.g., a merchant installing the app on their own store, who legitimately receives their own webhook deliveries and can observe the exact body+HMAC Shopify sent to the app's public webhook endpoint) can then send that identical body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` / `x-shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it never inspects the shop header, and `Registry.process` forwards the attacker-chosen shop value straight to the app's handler as `WebhookMetadata#shop`.

### Impact Explanation
This breaks the equality the app relies on: `hmac-signed body ⇔ shop that generated it`. A host application that uses `data.shop` (from `WebhookMetadata`) to look up per-tenant sessions, write incoming order/customer/inventory data, or otherwise scope processing to a tenant will process the attacker's payload under the identity of a victim shop chosen by the attacker. This is a cross-tenant confusion/access primitive: an attacker-controlled webhook body can be attributed to and processed under a different merchant's `shop` context purely because that field is excluded from the signed content, matching the report's underlying bug class of "a field acted on but not covered by the HMAC."

### Likelihood Explanation
Requires only: (1) the app's webhook endpoint be reachable over the internet (standard deployment for Shopify webhooks), and (2) the attacker have visibility into at least one legitimately-signed `(raw_body, hmac)` pair, which is trivial for any merchant who installs the app on their own store and observes their own webhook deliveries (e.g. via a proxy or logging). No access to `api_secret_key`, access tokens, or privileged accounts is needed.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the signed material used for HMAC verification, or otherwise cryptographically bind the shop domain to the payload before trusting it in `WebhookMetadata`. At minimum, `Webhooks::Request#to_signable_string` should not be limited to the raw body alone when the shop identity is later consumed by handlers as an authenticated fact.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker-shop.myshopify.com` and triggers a webhook event (e.g. `orders/create`), capturing the exact raw request body and the `x-shopify-hmac-sha256` value Shopify sent to the app's public webhook endpoint.
2. Attacker replays this identical HTTP request to the same webhook endpoint, but changes the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and finds it still matches, per [1](#0-0) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's payload, per [4](#0-3) , causing the host app to process attacker-controlled data under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
