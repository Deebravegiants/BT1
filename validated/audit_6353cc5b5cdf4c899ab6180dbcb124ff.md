Confirmed: `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb:36-38` returns only `@raw_body`, and `HmacValidator.validate_signature` in `lib/shopify_api/utils/hmac_validator.rb:26-31` computes and compares the HMAC over that signable string alone. The `shop` value returned by `Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`) comes from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in `to_signable_string` and therefore never covered by the HMAC check.

### Title
Webhook tenant identity (`shop`) is not bound to the HMAC signature, allowing cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. This breaks the equality that should hold between "the shop the HMAC authenticates" and "the shop the handler acts on," letting an attacker who controls (or has previously observed) any single valid `(raw_body, hmac)` pair replay it with an arbitrary `shop-domain` header value.

### Finding Description
`Registry.process` validates a webhook purely by checking the HMAC over the body: [1](#0-0) 

The HMAC is computed via `HmacValidator.validate`, which calls `validate_signature`, comparing `OpenSSL::HMAC.hexdigest` of `verifiable_query.to_signable_string` against the received signature: [2](#0-1) 

For webhook requests, `to_signable_string` returns only the raw body: [3](#0-2) 

Meanwhile, `shop` — the value the gem hands to the webhook handler as the tenant identity — is read directly from an unauthenticated header, with no cryptographic tie to the signed body: [4](#0-3) 

That value is then passed straight into the handler as the authoritative tenant identifier: [5](#0-4) 

So the binding "shop authenticated == shop acted on" does not hold: the HMAC authenticates `(body)`, but the code acts on `(body, shop-header)` where `shop-header` is unauthenticated. Any party capable of producing a valid `(body, hmac)` pair for one shop (e.g., their own shop, which they legitimately control as a merchant installing the app) can resend that exact same body/HMAC to the app's webhook endpoint with a different `x-shopify-shop-domain` header, and `HmacValidator.validate` will still return `true`, because the header is never part of `to_signable_string`.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate merchant of the app (and therefore able to receive real, validly-signed webhooks for their own shop) can cause the app to process that payload as if it originated from a different shop by swapping the `shop-domain` header on replay. Downstream host application logic that trusts `WebhookMetadata#shop` (as documented/intended usage of this gem) to select per-tenant records, credentials, or business state would then apply attacker-supplied webhook data to another tenant's context — a cross-tenant data injection primitive rooted entirely in this gem's validation logic, which authenticates the body but not the shop identity field it exposes to callers.

### Likelihood Explanation
Likelihood is constrained by the fact that the attacker still needs an initial valid `(body, hmac)` pair, which they can readily obtain by installing the app on their own shop and capturing any real webhook Shopify sends them (webhooks are frequent and easy to trigger by taking actions like updating an order/product in their own store). No possession of `api_secret_key`, access tokens, or any other shop's credentials is required — only replaying a header value that this gem never authenticates.

### Recommendation
Include the shop/tenant identifier (and ideally topic and webhook id) as part of the signed material verified against the HMAC, or otherwise cryptographically bind the `shop-domain` header to the payload before trusting it as a tenant identifier. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used as the sole tenant key without corroborating it via the API/webhook subscription that was registered for that specific shop's session.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers any webhook (e.g., `products/update`), capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — both are validly signed with the app's real secret.
2. Attacker resends this exact body and HMAC header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks the raw body (`lib/shopify_api/webhooks/request.rb:36-38`), never the `shop-domain` header.
4. The handler receives `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled body content under the victim's tenant context.

### Citations

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
