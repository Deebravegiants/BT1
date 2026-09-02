Found it. This is the strongest analog to the report's bug class: an "inconsistent binding" where the HMAC signature protects the request body, but a security-relevant field is read separately from an unauthenticated source and used to route/process the payload without being covered by that same signature.

### Title
Webhook `shop-domain` used for handler dispatch is never covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw HTTP body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to that signature [2](#0-1) . `Registry.process` validates the HMAC and, if it passes, dispatches the handler using `request.shop` taken from the unauthenticated header [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop_that_signed(body) == shop_delivered_to_handler`. Here, `HmacValidator.validate` only proves that `raw_body` was signed with the app's secret [4](#0-3) ; it says nothing about which shop's header value accompanied that body. Since `shop`, `topic`, `webhook_id`, and `api_version` are excluded from `to_signable_string`, any header value can be substituted without invalidating the HMAC (the HMAC is computed the same way by Shopify for every shop using the same request body content, e.g. `"{}"` for empty-body webhooks, or for any two webhooks whose bodies happen to collide). The gem then trusts `request.shop`, unverified, as tenant identity passed to the handler (`WebhookMetadata.new(... shop: request.shop ...)`).

### Impact Explanation
Because tenant identity (`shop`) is passed to the app's webhook handler unauthenticated, apps that rely on the gem's HMAC validation as a promise that `shop` is trustworthy will process/attribute webhook data to the wrong tenant if headers can be manipulated or replayed with a swapped `shop-domain` header alongside a valid signature computed on identical body bytes (e.g., empty or highly repetitive payloads). This is a cross-tenant data attribution / cross-tenant access risk in the qualifying impact category.

### Likelihood Explanation
Exploitability depends on the ability to produce two different `shop-domain` header values with the same signed HMAC-body pairing, which requires either a body/HMAC observed from any real webhook delivery (bodies are not secret) or bodies that are constant/predictable across shops (e.g., empty bodies, or delivery of a shared webhook body). This is a realistic scenario for topics with static or minimal payload content, making likelihood non-trivial but payload-dependent — assessed as Medium.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string (or otherwise cryptographically bind them, e.g. via a canonicalized header+body digest) so that the same HMAC cannot validate against an altered header set, matching the app's actual security assumption that a validated webhook's `shop` claim is trustworthy.

### Proof of Concept
1. Capture (or construct) any webhook delivery with raw body `"{}"` and its valid `x-shopify-hmac-sha256` header for `shop.myshopify.com` (as in `test/webhooks/registry_test.rb` lines 16-28) [5](#0-4) .
2. Replay the exact same body and HMAC header, but set `x-shopify-shop-domain` to a different shop's domain.
3. `Utils::HmacValidator.validate(request)` still returns `true` because the signature only covers `@raw_body` [1](#0-0) .
4. `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen domain [3](#0-2) , demonstrating the shop identity is not actually bound to the verified signature.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
