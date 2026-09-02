## Finding

### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) header fields are trusted without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `WebhookMetadata` built from `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` — all of which are taken verbatim from unauthenticated HTTP headers rather than from the HMAC-signed payload.

### Finding Description
`Webhooks::Request` implements the `VerifiableQuery` interface used by `Utils::HmacValidator`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., only the raw body) using `Context.api_secret_key`: [3](#0-2) 

`Registry.process` checks that this body-only HMAC is valid, then immediately trusts `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` — all sourced from headers (`shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, `shopify-webhook-id`) that are never part of the signed bytes — to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The identity binding broken here is: `HMAC(raw_body, api_secret_key) == received_hmac` is verified, but the equality that the handler actually relies on — `request.shop == the shop that produced this signed raw_body` — is never checked. Because only the body bytes are covered by the signature, an attacker who can influence or replay HTTP headers on the path to the handler (e.g., a reverse proxy/CDN misconfiguration, a shared endpoint serving multiple shops, or any component that forwards Shopify's signed body but lets headers be modified/duplicated) can pair a validly-signed body with an arbitrary `x-shopify-shop-domain`/`shopify-shop-domain` header. Since `Registry.process` never cross-checks the header-derived `shop` against anything bound to the signature, the handler receives attacker-controlled tenant attribution for otherwise-authentic webhook content, i.e., cross-tenant misattribution of webhook data.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` to select which shop's session/data to update in reaction to a webhook (the documented and expected use, per `docs/usage/webhooks.md`), an attacker who can manipulate the `shop-domain` header while a legitimately-signed body still validates can cause the app to process a genuine payload under a different tenant's identity — this is a cross-tenant boundary violation stemming directly from this gem's verification logic not binding the header fields it exposes as trusted to the signed bytes.

### Likelihood Explanation
Exploitation requires the attacker to be positioned to replay/relay a genuinely HMAC-signed webhook body while altering the accompanying headers (e.g., an intermediary, shared ingress, or any deployment where headers and body are not strictly bound together end-to-end before reaching this gem's `Registry.process`). This is a narrower path than a fully unauthenticated attack, but it is entirely a consequence of this gem's `to_signable_string` covering only `@raw_body` and not `shop`/`topic`/`webhook_id`/`api_version`, which the gem nonetheless treats as authenticated once `HmacValidator.validate` passes.

### Recommendation
Bind the metadata fields the handler relies on (at minimum `shop`) into the signable string used for HMAC verification, or otherwise require the caller to independently verify `request.shop` against a known/expected shop for the endpoint before trusting it. At minimum, document clearly that `shop`, `topic`, `webhook_id`, and `api_version` on `Webhooks::Request` are NOT covered by the HMAC and must not be trusted for tenant-identifying decisions without additional verification.

### Proof of Concept
1. Attacker (or a misconfigured intermediary under attacker influence) captures a legitimately Shopify-signed webhook request: raw body `B` with header `x-shopify-hmac-sha256: H` where `H = HMAC(secret, B)` and `x-shopify-shop-domain: shopA.myshopify.com`.
2. Attacker resends the same `B` and `H` but with `x-shopify-shop-domain: shopB.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes `HMAC(secret, B)` (body only) and it still matches `H`, so validation passes.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: request.shop` = `"shopB.myshopify.com"`, and the handler acts on shopB's tenant context using data that was actually signed/generated for shopA.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
