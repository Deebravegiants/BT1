## Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `WebhookMetadata` object built from headers that were never part of the signed material — most importantly `shop`. Any request that carries a previously‑captured, correctly‑signed body can be replayed with an arbitrary `shopify-shop-domain` header and will pass HMAC validation while claiming to originate from a different shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies only the body-based HMAC and then forwards `request.shop` unchanged into the handler payload: [3](#0-2) 

`HmacValidator.validate` computes and compares the digest strictly over `verifiable_query.to_signable_string` (the raw body for webhooks), so it never sees or constrains the `shop` header value: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop delivered to the handler`. Because `shop` is excluded from `to_signable_string`, that equality does not hold — the header can be swapped freely without invalidating the signature (the same shared `api_secret_key` signs webhooks for every shop that installs the app, so the signature alone doesn't bind to a specific tenant). This matches the report's underlying bug class: a value acted upon by downstream logic that is not covered by the authenticity check used to validate the whole message.

### Impact Explanation
Host applications built on top of `ShopifyAPI::Webhooks::Registry` (e.g. via `WebhookMetadata#shop`) commonly use the `shop` field to route webhook data to per-tenant records/sessions. Since `shop` isn't bound to the HMAC, a user who installs the app on their own store can capture one legitimately signed webhook (body + `x-shopify-hmac-sha256`) and replay it against the app's public webhook endpoint with the `shopify-shop-domain` header changed to a victim's shop domain. `Registry.process` will accept it as authentic and invoke the handler with attacker-chosen `shop`, `topic`, `webhook_id`, and `api_version` values, causing the host app to process/attribute data to the wrong tenant — a cross-tenant integrity violation.

### Likelihood Explanation
Any user who can install the app on at least one shop (a routine, unprivileged action) can capture a real webhook delivery for their own store and replay it to the same public webhook endpoint with modified headers. No access to `api_secret_key`, access tokens, or the target shop's credentials is required.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) as part of the material verified against the HMAC, or independently authenticate the shop domain against the app's known/installed shop list before trusting `request.shop` in `Registry.process`/`WebhookMetadata`. At minimum, document prominently in `Webhooks::Request` that `shop`, `topic`, `webhook_id`, and `api_version` are NOT covered by the HMAC and must not be trusted for tenant routing without additional verification (e.g., cross-checking against a stored session for that shop).

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and header `x-shopify-hmac-sha256: H`.
2. Replay to the app's webhook endpoint:
```
POST /webhooks HTTP/1.1
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim.myshopify.com
x-shopify-api-version: 2024-01

B
```
3. `HmacValidator.validate` succeeds because `H` was computed only over `B`, which is unchanged. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload actually originated from `attacker.myshopify.com`.

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
