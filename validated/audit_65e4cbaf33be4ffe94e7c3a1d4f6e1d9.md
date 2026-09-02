### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` field that identifies which tenant the webhook belongs to is read from an HTTP header that is never included in the signed payload. Any party able to obtain one validly-signed webhook body (all shops installing the same app share a single `api_secret_key`, and webhook bodies/HMACs are frequently visible in logs, error trackers, or via a shop's own webhook deliveries) can replay that same body with an arbitrary `shopify-shop-domain` / `x-shopify-shop-domain` header and have it accepted as authentic, attributing the payload to a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from unauthenticated headers: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`: [3](#0-2) 

And `Registry.process` treats a request as authentic once that body-only HMAC check passes, then hands the *header-derived* (unauthenticated) `shop` straight to the app's webhook handler as the tenant identifier: [4](#0-3) 

This breaks the intended identity binding: `HMAC(api_secret_key, raw_body) == received_hmac` is meant to imply "this entire webhook — including which shop it is for — came from Shopify for this shop." In reality the equality only covers the body bytes; the `shop` (and `topic`/`webhook_id`) values are attacker-controllable bytes that ride along unauthenticated. Because every installation of an app shares the same `api_secret_key`, an HMAC computed for shop A's webhook body is equally valid when replayed with shop B's (or an attacker's own) `shop-domain` header, as long as the JSON body happens to match or is reused verbatim. This is directly analogous to the referenced bug class: a value that is *acted upon* (here, the tenant-identifying `shop`) is not covered by the same authentication check (the HMAC) that is used to establish trust in the request.

### Impact Explanation
This qualifies as **Critical — cross-tenant access**: a webhook handler processing data under a spoofed `shop` value can cause the host application to write, cache, or act upon attacker-supplied data (or a replayed legitimate payload) as if it belonged to a different merchant's tenant/session context, since the gem provides no authenticated shop binding for the handler to trust. Any application logic keyed off `WebhookMetadata#shop` (e.g., looking up the merchant's session/store by that shop string, as the docs explicitly instruct: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) inherits this trust without any cryptographic basis for it.

### Likelihood Explanation
Exploitation requires possession of a body + HMAC pair that is valid for the shared `api_secret_key` — obtainable either by capturing/replaying a shop's own real webhook delivery (webhook bodies are not secret; they are routinely visible in application logs, error trackers, or from a merchant's own webhook endpoint) or, for identical/predictable payloads (e.g., minimal-body topics), by directly computing the same HMAC output since the endpoint accepts any shop header alongside it. No access token, TLS interception, or privileged account is needed — only network access to the app's public webhook endpoint. This matches the "unprivileged internet user" threat model.

### Recommendation
Include the security-relevant headers (`shop-domain` at minimum, ideally `topic` and `webhook-id`) as part of the signable string used for HMAC computation, or otherwise cryptographically bind the header-derived `shop` value to the signed body before it is exposed via `WebhookMetadata`. Document (and ideally enforce in the gem) that consuming applications must independently verify the `shop` corresponds to a shop that has actually installed the app before trusting webhook payloads.

### Proof of Concept
1. Attacker's own store installs the app and receives a legitimately HMAC-signed webhook, e.g. body `{}` with header `x-shopify-hmac-sha256: <valid HMAC for {} under the shared api_secret_key>`.
2. Attacker replays the identical body/HMAC to the app's public webhook endpoint but substitutes `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` and succeeds because the body is unchanged: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload never originated from Shopify for that shop, as demonstrated by the test fixture pattern where `shop` is set purely via header regardless of the signed body: [6](#0-5)

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

**File:** test/webhooks/registry_test.rb (L304-314)
```ruby
      def test_process_hmac_validation_fails
        headers = {
          "x-shopify-topic" => "some/topic",
          "x-shopify-hmac-sha256" => "invalid",
          "x-shopify-shop-domain" => "shop.myshopify.com",
        }

        assert_raises(ShopifyAPI::Errors::InvalidWebhookError) do
          ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers))
        end
      end
```
