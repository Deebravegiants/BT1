This confirms the analog: the webhook `hmac` covers only the request body, and the `shop` value used to identify the tenant comes from an HTTP header that is entirely outside the HMAC-signed content.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header values are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` validates is computed only over the raw request body via `to_signable_string`. Because the header is never part of the signed content, an attacker who controls the delivery of the HTTP request (e.g., replays a captured, validly-signed webhook body verbatim, or is a party that can influence headers between Shopify's edge and the app, such as a shared reverse proxy/CDN/load balancer configuration) can present a legitimately-signed body together with an arbitrary `shop-domain` header value and have it be treated as authenticated for that different tenant.

### Finding Description
The equality that should be enforced is: `shop value used by the app to load/act on tenant data == shop value that was actually cryptographically bound to the authenticated payload`. Instead:

- `Utils::HmacValidator.validate` verifies the HMAC over `verifiable_query.to_signable_string`.
- For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [1](#0-0) 
- The `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are covered by the signature: [2](#0-1) 
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body-only HMAC) and then dispatches the handler using `request.shop`, `request.topic`, and `request.webhook_id` taken from the unauthenticated headers: [3](#0-2) 

So the `hmac` bytes verified (body only) do not equal the bytes actually parsed and acted upon (body + shop/topic/webhook_id headers) — the same class of bug as the Centrifuge router issue where the on-chain authorization check (`isOperator`) held true, but the value it was implicitly trusting (`owner`/`controller`) was never actually bound to the authenticated caller.

### Impact Explanation
This breaks the shop/tenant identity binding relied upon by every app built on this gem's webhook handling: `Registry.process` passes `request.shop` into `WebhookMetadata` and to the handler as ground truth for which merchant the event belongs to: [4](#0-3)  If any component between Shopify and the app (or a replayed/relayed request) can supply a body with a valid signature but a different `shop-domain` header, the app will process data under the wrong tenant identity — a cross-tenant confusion that matches the Critical impact category ("cross-tenant access").

### Likelihood Explanation
Exploitation requires the attacker to supply an HTTP request with a body that has a valid HMAC (e.g., a captured/replayed genuine webhook payload for topic-body combinations that don't vary per shop, or any setup where headers can be rewritten downstream of Shopify's signing) while controlling/rewriting the `shopify-shop-domain` header before it reaches the app's webhook endpoint. This is not a purely theoretical gap: the signing scope (body-only) is a documented Shopify webhook property, but this gem's implementation treats the header-derived `shop` as equally trustworthy as the signed body when handing it to application handlers, without ever binding it into the signature check.

### Recommendation
Do not treat `request.shop` (or `topic`/`webhook_id`) as authenticated merely because `Utils::HmacValidator.validate(request)` passed. Either:
- Document explicitly that `shop`, `topic`, and other headers are unauthenticated metadata and must be independently corroborated (e.g., cross-checked against a known/installed shop list) before being trusted by the handler, or
- Include the relevant headers (at minimum `shop-domain`) in the signable content used for verification, if Shopify's webhook signing were extended to cover them, or require the app to reconcile the header-derived shop against the shop encoded in `parsed_body` (Shopify webhook payloads typically include a shop-scoped identifier) before dispatch.

### Proof of Concept
1. Register a webhook handler for topic `orders/create` that trusts `data.shop` from `WebhookMetadata` to look up per-tenant credentials/state.
2. Capture (or otherwise obtain) one legitimately Shopify-signed webhook request body+HMAC for shop A, topic `orders/create`.
3. Replay/forward the identical raw body and `shopify-hmac-sha256` value to the app's webhook endpoint, but with the `shopify-shop-domain` header changed to shop B.
4. `Utils::HmacValidator.validate` succeeds because it only checks the raw body against the HMAC, which is unchanged: [5](#0-4) 
5. `Registry.process` dispatches the handler with `request.shop` == shop B even though the signed body was never associated with shop B by Shopify: [6](#0-5)

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
