## Finding

### Title
Webhook shop-tenant identity spoofing via HMAC that only binds the request body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value that is handed to application webhook handlers directly from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` checks is computed only over the raw request body. The library therefore authenticates that *the body bytes* came from Shopify (using the app's shared secret) but never authenticates that the accompanying `shop` (or `topic`/`webhook-id`) header actually belongs to the tenant that produced that body. This breaks the intended binding `verified_hmac == (body, shop)` down to `verified_hmac == body`.

### Finding Description
`HmacValidator.validate` computes and compares the signature solely against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw JSON body, and the `shop` accessor is read straight from the (attacker-controllable, header-level) `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the HMAC: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (together with `request.topic` and `request.webhook_id`, which are equally unauthenticated) when building the metadata handed to the host application's handler: [4](#0-3) 

Because the HMAC only commits to the body bytes, any previously-observed, genuinely-signed webhook delivery (for example one the attacker legitimately received for their own store, since a public app installed on an attacker-controlled shop will deliver real, correctly-signed webhooks to that shop's own endpoint) can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header swapped to a victim shop's domain. The signature remains valid because it never covered the header, yet `WebhookMetadata#shop` will report the victim's domain to the host application's handler.

### Impact Explanation
Host applications built on this gem are documented to use `WebhookMetadata#shop` as the tenant key for locating/updating per-shop records (this is the gem's whole reason for exposing `shop` on the metadata object). An attacker who can obtain any one genuinely-signed webhook delivery (trivial for a public app: install it on an attacker-owned development store) can replay that payload while relabeling it as belonging to a different merchant's shop domain. Since the HMAC check passes, the host app will process attacker-supplied (though "genuine" in origin) webhook data attributed to a shop the attacker does not control — a cross-tenant data-integrity/isolation break, matching the "cross-tenant access" impact class.

### Likelihood Explanation
No access token, `client_secret`, or privileged credentials are required. The only prerequisite is the ability to receive at least one legitimate webhook delivery from the target app (attainable by installing a public app on an attacker-controlled store) and the ability to POST arbitrary headers/body to the app's public webhook endpoint, which by design accepts unauthenticated internet traffic. This is a realistic, low-effort attack path for any unprivileged user of a public Shopify app.

### Recommendation
Extend `to_signable_string` for `ShopifyAPI::Webhooks::Request` (or add a separate binding check in `Registry.process`) so the HMAC-covered signable string incorporates the header fields that are subsequently trusted as identity (`shop`, `topic`, `webhook_id`), matching Shopify's actual webhook-verification guidance of pinning the `shop` to session/tenant storage rather than trusting the header value in isolation. At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must be cross-checked by the host application against its own tenant records before being trusted as an identity key.

### Proof of Concept
1. Install the target public app on an attacker-owned store `attacker-shop.myshopify.com`; capture a genuine webhook delivery, e.g. `orders/create`, with header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, valid `X-Shopify-Hmac-Sha256`, and JSON body `B`.
2. Replay the exact same body `B` and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only recomputes the signature over `B` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` invokes the host handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host application to apply attacker-originated data under the victim tenant's identity.

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
