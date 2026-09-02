### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing shop-spoofing of otherwise-valid webhook payloads - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` used to route and label a processed webhook from the `shopify-shop-domain` HTTP header, but the HMAC signature verified by `Utils::HmacValidator` only covers the raw request body — never the headers. This breaks the binding "shop attributed to the webhook == shop the HMAC was computed for," letting anyone who can present a body+HMAC pair that validates (e.g. one legitimately produced by Shopify for their own shop/store, or any body for which they can compute a valid HMAC using a leaked/guessed secret elsewhere) attach an arbitrary `shop` value to it.

### Finding Description
`HmacValidator.validate` computes the digest over `verifiable_query.to_signable_string` and compares it against `verifiable_query.hmac`: [1](#0-0) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, and `hmac` is read from the `hmac-sha256` header; but `shop` is read from a completely separate, unauthenticated header (`shopify-shop-domain` / `x-shopify-shop-domain`): [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then unconditionally trusts `request.shop` (derived from the unsigned header) to build the `WebhookMetadata` passed into the app's webhook handler: [3](#0-2) 

So the equality that should hold — "shop bound into the verified signature == shop acted upon by the handler" — does not: the HMAC only binds the *body bytes*, while the shop identity used downstream comes from a header that is never part of the signed material. Any caller that can produce a body/HMAC pair that passes verification (the HMAC secret is the app's `client_secret`, which Shopify's genuine webhook deliveries satisfy) can also set `shopify-shop-domain` to any value, and `Registry.process` will treat the payload as belonging to that attacker-chosen shop.

### Impact Explanation
This crosses a tenant boundary inside a multi-tenant app: a webhook payload correctly signed for shop A can be replayed/relayed to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to shop B, and the gem will still report `HmacValidator.validate` == true and hand the handler a `WebhookMetadata` claiming the event is for shop B. Any host application that uses `WebhookMetadata#shop` (as documented) to look up the shop's session/access token or to write shop-scoped data will act on the wrong tenant, i.e. cross-tenant data confusion driven entirely by the shape of this gem's `Request`/`Registry` API, without needing the app's `client_secret` to be leaked.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs a body+HMAC that validates for the target endpoint's secret — this is trivially satisfiable if the attacker owns any shop that installs the app (their own legitimately signed webhooks), since the header can then be freely rewritten before delivery to the same endpoint, or if any webhook payload/HMAC pair is replayable across shops. No credential theft, TLS interception, or privileged access is required.

### Recommendation
Include the shop-domain header (and any other header consumed as identity, e.g. `topic`) in the bytes that are HMAC-verified, or otherwise cryptographically bind `shop` to the signed body (e.g. verify shop against a session/lookup keyed independently of the header) before constructing `WebhookMetadata`. At minimum, `Registry.process` should not trust `request.shop` when the HMAC only guarantees body integrity, not header integrity.

### Proof of Concept
1. Attacker controls an app-installed shop `attacker.myshopify.com` and receives a legitimately Shopify-signed webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for the app's `client_secret`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the same `raw_body: B` and `hmac-sha256: H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` reads `H` unchanged; `to_signable_string` returns `B` unchanged, so `Utils::HmacValidator.validate` [4](#0-3)  still returns `true`.
4. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: request.parsed_body, ...)` [5](#0-4) , even though the payload was never actually signed for `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
