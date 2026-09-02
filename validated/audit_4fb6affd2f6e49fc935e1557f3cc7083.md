### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content solely from the raw request body, while the `shop`, `topic`, and `webhook_id` values that are handed to app webhook handlers are read from HTTP headers that are never included in that signable content. `Utils::HmacValidator.validate` only proves that the *body* matches the signature — it says nothing about the headers — so any attacker who can influence or replay the headers accompanying an otherwise validly-signed body can misattribute the payload to an arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers, none of which are part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (here, just the raw body) against the supplied HMAC: [3](#0-2) 

`Registry.process` trusts this validation, then forwards the header-derived `shop` (and `topic`/`webhook_id`) straight to the handler as the authoritative tenant identifier for the delivered payload: [4](#0-3) 

The identity binding that should hold is: *the shop asserted in `WebhookMetadata.shop` == the shop for which Shopify actually generated and HMAC-signed this exact delivery*. Because the HMAC covers only the body bytes and not the header claiming which shop the body belongs to, this equality is never actually checked — the `shop-domain` (and `topic`/`webhook-id`) header can be swapped for a different value while the signature remains valid, since the signature was computed over the body alone.

### Impact Explanation
A host application built on this gem receives `WebhookMetadata#shop` as the trusted tenant key for dispatching webhook side effects (e.g., updating shop-scoped records, revoking access, provisioning data) inside `handler.handle`. If an attacker who controls one legitimately-signed webhook delivery (for example, for their own installed shop) can cause the app to instead process it while asserting a different shop's domain in the header, the app will apply that webhook's body content to the wrong tenant's data — a cross-tenant confusion condition. This matches the Critical "cross-tenant access" impact category, since the header/body binding that the app relies on for tenant isolation is not actually enforced by this gem's signature check.

### Likelihood Explanation
Exploitation is not gated by exchange with Shopify's genuine delivery infra directly, since the vulnerable surface is the gem's own verification: any request reaching the host app's registered webhook endpoint with a body/HMAC pair that once was valid for shop A, but headers rewritten to claim shop B, still passes `HmacValidator.validate` because those headers are outside the signable content entirely. This requires no `api_secret_key`, access token, or other secret — only observation/interception of one legitimately delivered webhook body+HMAC pair (or use of a topic/body combination shared/predictable across shops), then re-submission with modified headers to the app's own public webhook endpoint.

### Recommendation
Include the shop domain, topic, and webhook id in the HMAC-covered signable content (e.g., by having `to_signable_string` incorporate these header values alongside the body, or by validating them against an independently-authenticated source such as a stored, previously-established session/shop mapping) so that the values passed into `WebhookMetadata` cannot be forged independently of the signed payload.

### Proof of Concept
1. Capture one legitimately delivered webhook for `shop-a.myshopify.com`: raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H`, computed as `HMAC-SHA256(secret, B)`.
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `X-Shopify-Shop-Domain` with `shop-b.myshopify.com` (and/or altering `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers, and `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `B`, which is unchanged. [5](#0-4) 
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed_body, ...)`, causing the app to apply shop-a's webhook payload as if it belonged to shop-b.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
