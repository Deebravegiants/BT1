Confirmed: `Registry.process` at [1](#0-0)  validates only the HMAC and then trusts `request.topic` and `request.shop` (both header-derived, unauthenticated) to build `WebhookMetadata` passed to the handler.

### Title
Webhook HMAC signs only the body, not the `shop`/`topic` headers, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator` verifies the HMAC exclusively against that body. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Registry.process` and handed to application webhook handlers as trusted tenant/topic identifiers come from HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`HmacValidator.validate` computes the HMAC solely over that signable string and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` only checks this body HMAC before dispatching to the handler using the header-derived `shop` and `topic`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from HTTP headers with no cryptographic binding to the signed body: [4](#0-3) 

Because the `api_secret_key` HMAC key is a single value shared by the app across **all** shops that install it (there is one `Context.api_secret_key`, not a per-shop key), a merchant who installs the app on their own shop receives genuinely-signed `(body, hmac)` pairs. Since `shop` and `topic` are outside the signed content, that same valid `(body, hmac)` pair can be replayed to the app's webhook endpoint with the `shopify-shop-domain` and `shopify-topic` headers changed to any other shop and any topic (e.g., a victim shop and `shop/redact`, `app/uninstalled`, `orders/create`). The equality the code implicitly relies on — "HMAC-authenticated bytes" == "the shop/topic the handler acts on" — does not hold, because the shop and topic are parsed from unauthenticated bytes while only the body is verified.

### Impact Explanation
This lets an unprivileged holder of one valid webhook signature (obtainable by installing/uninstalling the app on their own store, a normal unprivileged action) forge webhook deliveries attributed to an arbitrary victim shop and arbitrary topic, without needing the app's `api_secret_key`, an access token, or any privileged credential. Depending on the host application's webhook handler logic, this enables cross-tenant data manipulation (e.g., triggering GDPR redaction handlers, order-processing side effects, or app-uninstall cleanup logic) against a shop the attacker does not control — a cross-tenant integrity/authorization violation stemming directly from this gem's signature scope.

### Likelihood Explanation
Moderate-to-high: the attacker only needs to install the target app on any shop they control (or intercept one legitimate delivery to their own shop) to obtain a valid `(raw_body, hmac)` pair, then send an HTTP POST to the victim app's webhook endpoint with spoofed `shopify-shop-domain`/`shopify-topic` headers and the captured body/HMAC unchanged. No secrets, tokens, or privileged access are required.

### Recommendation
- **Short term:** Bind the `shop`, `topic`, `webhook_id`, and `api_version` header values into the signed material verified by `HmacValidator`, or otherwise validate that the header-derived shop domain is one the host application expects for the delivery it is processing, before trusting them in `Registry.process`/`WebhookMetadata`. Document clearly that the vendor's HMAC only covers the body so host applications are not misled into trusting headers as authenticated.
- **Long term:** Review every gadget/module in this gem where a value is read from an unauthenticated channel (headers, query params) but later treated as a trusted identity or tenant key, and ensure identity-bearing fields are always covered by an authenticated binding.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and captures one legitimate webhook delivery (raw body `B`, header `x-shopify-hmac-sha256: H`) for topic `orders/create` — a normal, unprivileged action.
2. Attacker sends a POST to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid because HMAC only covers `B`)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (spoofed)
   - `x-shopify-topic: shop/redact` (spoofed to any registered topic)
3. `Utils::HmacValidator.validate(request)` succeeds because it only re-derives the HMAC from `B` [5](#0-4) .
4. `Registry.process` dispatches to the `shop/redact` handler with `shop: "victim-shop.myshopify.com"` [6](#0-5) , causing the host application to act on the victim shop's data under a spoofed, unauthenticated identity claim.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
