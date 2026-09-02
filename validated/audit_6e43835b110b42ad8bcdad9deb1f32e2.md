This confirms the finding. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, but that validation only covers `request.to_signable_string`, which for `Request` returns just `@raw_body` [1](#0-0) . The `shop` value is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is never included in that signable string, nor otherwise cross-checked [2](#0-1) . Yet `Registry.process` passes this unauthenticated header value directly into `WebhookMetadata.shop`, which is the tenant-identifying field handed to the app's `handler.handle` [3](#0-2) [4](#0-3) . The gem's own docs confirm `data.shop` is meant to identify "the shop domain of the webhook" and is the field apps use to route/attribute the payload to a merchant [5](#0-4) .

### Title
Webhook `shop` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a request as authentically originating from Shopify for a given shop once `Utils::HmacValidator.validate(request)` passes. However, that HMAC only signs the raw request body; the `shop` (and `topic`/`webhook_id`/`api_version`) headers are excluded from the signed payload. Any party who has ever obtained one valid `(raw_body, hmac)` pair for a webhook topic (e.g., from a webhook they legitimately received for a shop they installed the app on) can replay it against the app's public webhook endpoint with the `shopify-shop-domain` header rewritten to name a different (victim) merchant's shop domain. The HMAC still validates because it only checked body bytes, but the app processes the payload as if it belongs to the victim shop.

### Finding Description
`HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string` [6](#0-5) . For webhook requests, `to_signable_string` is defined as simply the raw body:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

Meanwhile `shop` is parsed straight from a header with no relationship to the signed bytes:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`Registry.process` only verifies the HMAC and then forwards `request.shop` unchecked into `WebhookMetadata`, which is delivered to the app's handler as the authoritative tenant identifier:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

The identity binding this breaks: the shop bytes covered by the HMAC (none — the signature covers only body content) versus the shop bytes acted on by `Registry.process`/`WebhookHandler.handle` (the unauthenticated `shop-domain` header). An attacker never needs `api_secret_key`; they only need one legitimate `(body, hmac)` pair, which they can obtain themselves by installing the app on their own store and receiving one real webhook delivery for any registered topic. They then POST that same body/hmac to the app's public webhook endpoint with `shopify-shop-domain` (or `x-shopify-shop-domain`) set to the victim shop's domain (and optionally a different `webhook_id`, since that also isn't signed, to bypass idempotency checks).

### Impact Explanation
This lets an unprivileged internet user (who merely has app access to their own shop) forge webhook events attributed to a different merchant, i.e., cross-tenant data injection/confusion at the gem's trust boundary. Applications built on this gem key their persistence, deduplication, and business logic (order processing, uninstall handling, GDPR redact flows, etc.) off `data.shop` as documented by the gem itself, so a forged shop value causes the host app to act on behalf of, or write data under, a tenant the attacker does not control access to — matching the "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is high for any app that has processed at least one real webhook: capturing a `(raw_body, hmac)` pair requires only normal app installation on the attacker's own store (no secret key, no privileged access), and the replay itself is a trivial HTTP POST with modified headers against the public webhook callback URL that every installed app must expose.

### Recommendation
Include `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind the shop domain to the payload before trusting it. At minimum, `Registry.process`/`WebhookMetadata` should not treat the `shop-domain` header as authoritative for tenant identity unless it is verified as part of the signed content (e.g., cross-checking it against a `shop`/`admin_graphql_api_id` domain embedded in the signed JSON body where the topic guarantees one is present).

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` and register for a webhook topic (e.g. `orders/create`).
2. Capture one real delivery from Shopify: raw body `B` and header `shopify-hmac-sha256: H` (valid for `B` under the app's `api_secret_key`, but the attacker never sees the secret itself).
3. Send a new POST to the app's webhook endpoint with the same body `B` and the same `shopify-hmac-sha256: H`, but set `shopify-shop-domain: victim-shop.myshopify.com` (and change `shopify-webhook-id` to a fresh value to avoid dedupe).
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because it only checks `B` against `H` [7](#0-6) .
5. `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host app to process attacker-controlled data as if it came from the victim shop [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
