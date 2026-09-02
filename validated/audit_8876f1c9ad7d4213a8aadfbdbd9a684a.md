This confirms the finding. The `WebhookMetadata.shop` field, which the merchant's application uses to identify which tenant/shop a webhook belongs to, is sourced entirely from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, while the HMAC signature only covers the raw request body.

### Title
Webhook shop-domain header is not covered by HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` attribute — used downstream to identify which merchant a webhook event belongs to — is read from an HTTP header that is never included in the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/verifies the HMAC exclusively against that signable string [2](#0-1) . Meanwhile, `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , a field that is never mixed into the signed bytes. `Registry.process` validates only the HMAC of the body and then forwards `request.shop` unchanged into `WebhookMetadata`, which is the sole tenant identifier passed to the host application's handler [4](#0-3) [5](#0-4) . This breaks the intended binding `hmac == HMAC(secret, body ∥ shop)`, reducing it to `hmac == HMAC(secret, body)`, i.e. the `shop` claimed by the request is never bound to the signature that authenticates it.

### Impact Explanation
Because `shop` is unauthenticated, any topic whose body content is fixed, predictable, or shared across shops (e.g., empty-body topics, or topics whose JSON payload does not embed the originating shop) yields an HMAC that is valid regardless of which `shop-domain` header accompanies it. An attacker who can obtain one valid `(body, hmac)` pair — for instance via a replayed or observed webhook delivery, or a topic with deterministic content — can resubmit that exact body/HMAC combination to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. The application's handler will process the event as if it originated from a different, attacker-chosen merchant, resulting in cross-tenant data confusion/processing (e.g., a `shop/redact` or `customers/redact` GDPR webhook, or a business-logic webhook, being executed against the wrong tenant's data).

### Likelihood Explanation
Exploitation requires the attacker to already possess a validly-signed `(body, hmac)` pair for some topic — which is plausible for topics with static/empty bodies or via replay of a previously captured delivery — but does not require the `api_secret_key` itself. This keeps likelihood at Medium: it's a genuine architectural gap (signature doesn't bind the tenant claim) rather than a trivially always-exploitable bug for every topic.

### Recommendation
Include the `shop` (and ideally `topic`) values in the string that is HMAC-verified, or otherwise cryptographically bind the shop-domain header to the signed payload, so that `HmacValidator.validate` fails whenever the shop claimed by the request headers differs from the shop the signature was actually generated for.

### Proof of Concept
1. Capture (or predict) a valid `(raw_body, hmac)` pair for a webhook topic with a static/empty body, e.g. `raw_body = "{}"` and its corresponding `x-shopify-hmac-sha256` value, as constructed in [6](#0-5) .
2. Send a request to the app's webhook endpoint with the same `raw_body`/`hmac`, but set `x-shopify-shop-domain` to a different merchant's shop domain.
3. `Utils::HmacValidator.validate` returns `true` because it never inspects the `shop` header [7](#0-6) .
4. `Registry.process` forwards the forged `shop` value straight into the handler via `WebhookMetadata`, causing the event to be attributed to the wrong tenant [8](#0-7) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
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
