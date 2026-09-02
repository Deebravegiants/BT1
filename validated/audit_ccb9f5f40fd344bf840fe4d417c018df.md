### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` uses the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header to populate the `shop` value that is handed to the host application's webhook handler. Because the HMAC never covers the shop-domain header, an attacker who has received one legitimate, validly-signed webhook (e.g. for their own store) can resend that exact body/HMAC pair while substituting the shop-domain header for a victim shop, and the library will report the request as valid and dispatch it as if it originated from the victim.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares an HMAC purely over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body, and `shop` is read straight from a request header with no cryptographic binding to that body: [2](#0-1) [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the request (i.e., only the body), then immediately trusts `request.shop` (the unauthenticated header) as the tenant identity when building `WebhookMetadata` for the handler: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated == shop the body is attributed to` does not hold. The equality actually enforced is only `HMAC(raw_body) == received_hmac`; the `shop` header is fully attacker-controlled independent of that check. Any party that can obtain one legitimate webhook delivery (e.g., an attacker who installs the host app on their own store and thus legitimately receives webhooks with valid HMACs for their own shop) can replay the identical `raw_body` + `hmac-sha256` header to the same endpoint while swapping the `shop-domain` header to a different (victim) shop domain. `Registry.process` will still consider the HMAC valid (since it only checks the body) and will dispatch `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own body>, ...)` to the host application's handler.

### Impact Explanation
This is a cross-tenant confusion vulnerability: the library allows an attacker to make the host application believe attacker-controlled webhook content pertains to a shop the attacker does not own/control. Depending on how the host app's `WebhookHandler.handle` uses `data.shop` (e.g., to look up per-shop credentials, update per-shop records, trigger per-shop business logic such as order/inventory sync, or key a job queue as shown in the gem's own documented usage `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this enables an attacker to inject forged data attributed to a victim tenant — a cross-tenant access/identity-binding bypass, since the gem is the layer responsible for asserting request authenticity and shop attribution before handing data to the app.

### Likelihood Explanation
Exploitation only requires the attacker to be a normal, unprivileged installer of the host app (to receive one legitimately-HMAC'd webhook for their own store) and the ability to send arbitrary HTTP POST requests to the app's public webhook endpoint with custom headers — no access token, `client_secret`, or privileged account is required. The HMAC secret (`api_secret_key`) is never exposed to the attacker; they merely replay a signature that was computed for content they legitimately received.

### Recommendation
Include the shop-domain (and other identity-relevant headers such as topic and API version, if used for dispatch) inside the HMAC-covered signable data, or independently verify that the shop-domain header corresponds to a shop with an existing, expected relationship to the app before trusting it, rather than trusting an unauthenticated header field as tenant identity in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the host app on their own store `attacker-shop.myshopify.com` and configures a webhook (e.g., `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with a body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`, and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact `raw_body` and `hmac-sha256` header value.
4. Attacker sends a new POST request to the same webhook endpoint with the identical `raw_body` and `hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` re-computes the HMAC over `raw_body` only, which still matches `H`, so validation passes.
6. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)` to the host app's handler, which now processes attacker-supplied data as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
