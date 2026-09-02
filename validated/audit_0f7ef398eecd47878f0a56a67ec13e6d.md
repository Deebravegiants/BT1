## Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook confusion - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes the value used for HMAC verification from the raw body alone, while the `shop` identity that gets handed to the app's webhook handler is read from an unauthenticated header. This breaks the binding `hmac(raw_body) == hmac(raw_body)` **for shop = shop-that-sent-the-body**, i.e. the signature never establishes `signed_content ⊇ shop`. An attacker who legitimately receives a correctly-signed webhook for their own shop can replay the exact same bytes to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header for a victim shop; the signature still validates and the handler processes the payload as if it came from the victim tenant.

## Finding Description
`Request#to_signable_string` only returns the raw HTTP body: [1](#0-0) 

`Request#shop` is read straight from a header with no cryptographic tie to the body or to the HMAC: [2](#0-1) 

`HmacValidator.validate` verifies exactly (and only) `to_signable_string` against the received `hmac`: [3](#0-2) 

`Registry.process` gates on this HMAC check and then forwards `request.shop` (the unauthenticated header) directly into the data passed to the app's handler: [4](#0-3) 

Because the HMAC covers only the body bytes and never the shop identity, the equality the code actually enforces is:

`HMAC_secret(raw_body) == received_hmac`

but the identity binding the app relies on for tenant isolation is implicitly assumed to be:

`shop_header == shop_that_Shopify_actually_signed_this_body_for`

These are not the same guarantee. Any two webhooks with identical bodies (e.g., a shop-scoped event whose payload doesn't embed the shop, or simply the attacker's own legitimately-received webhook) are interchangeable across the `shop-domain` header without invalidating the signature, since that header is never part of `to_signable_string`.

## Impact Explanation
This is a cross-tenant identity-binding break: an attacker who operates (or installs the app on) their own shop can capture a genuine, correctly-signed webhook and re-POST it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. The `HmacValidator` still reports the request as valid, and `WebhookMetadata.shop` (and therefore the handler's per-tenant logic, e.g., looking up/updating data keyed by shop) is executed with attacker-chosen tenant identity. Depending on the handler, this can lead to data being written into, or actions taken against, another merchant's tenant — a cross-tenant access impact.

## Likelihood Explanation
Exploitation only requires the attacker to be a normal, unprivileged user of the app (install the app on a shop they control to receive at least one legitimately-signed webhook), plus the ability to POST to the app's public webhook endpoint with custom headers — no access token, `client_secret`, or leaked credential is needed. This is reachable purely through this gem's own webhook verification API (`Webhooks::Request` + `Webhooks::Registry.process`).

## Recommendation
Bind the shop identity into the signed content that `HmacValidator` verifies, or otherwise cryptographically tie the `shop-domain` header to the signature (e.g., include shop in the value passed to `to_signable_string`, or independently confirm the shop against a value derived from data that *is* covered by the HMAC, such as a shop id embedded in the parsed/verified body). At minimum, document that `request.shop` must not be trusted for tenant routing unless corroborated by out-of-band means, and provide an API that lets consumers verify shop-to-signature binding.

## Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, headers include `X-Shopify-Hmac-Sha256: H` (valid for `B`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (HMAC `H` and body `B` unchanged).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: replayed_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(B) == H`.
4. `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` is delivered to the app's handler, which acts on data intended for `attacker-shop` but attributed to `victim-shop`. [5](#0-4) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
