### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute directly from the unauthenticated `shopify-shop-domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body (`to_signable_string` returns `@raw_body`). Because the identity of the tenant (`shop`) is never included in the signed material, a valid signature for one shop's webhook payload can be replayed with a forged `shop-domain` header to impersonate a different shop.

### Finding Description
The equality this breaks: `shop authenticated by the app == shop bound inside the HMAC-signed bytes`. In this gem the left side is `request.shop` (read from `shopify-shop-domain`/`x-shopify-shop-domain` header) [1](#0-0)  while the right side — the bytes actually covered by the HMAC — is only `@raw_body`: [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` and then trusts `request.shop` verbatim when building `WebhookMetadata` passed to the host app's handler: [3](#0-2) . `HmacValidator.validate` computes/compares the signature purely against `verifiable_query.to_signable_string` (i.e. the raw body), never mixing in the shop domain: [4](#0-3) . `WebhookMetadata.shop` is a plain, unauthenticated string field forwarded straight to the handler: [5](#0-4) .

Because the webhook HMAC secret (`api_secret_key`/`client_secret`) is shared across every shop that has the app installed (it is the app's secret, not a per-shop secret), a valid `(body, hmac)` pair obtained from *any* shop that legitimately has the app installed remains cryptographically valid when replayed with a different `shop-domain` header value.

### Impact Explanation
This is a cross-tenant data-integrity break: a user who controls one tenant (e.g. their own free/dev store with the app installed) can generate a webhook with a body they influence (e.g. creating an order/customer/product with attacker-chosen content) and receive a validly-HMAC'd delivery from Shopify. They can then replay that exact body+HMAC directly to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. `Registry.process` will pass HMAC validation (since only the body is checked) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that trusts `data.shop` to select which tenant's records to create/update/delete (a documented, expected usage pattern of this field) will act on attacker-supplied content under the victim's identity — i.e., cross-tenant data injection/manipulation without ever needing the victim's credentials.

### Likelihood Explanation
Requires only: (1) the ability to install the app on some shop (trivial for public/dev-store apps), (2) triggering any webhook topic the app subscribes to, and (3) sending a raw HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header — no credentials, tokens, or privileged access to the victim shop are needed. The webhook endpoint is by design internet-reachable and unauthenticated apart from the HMAC.

### Recommendation
Bind the shop identity into the verified material: either include the shop domain in the HMAC-signed string, or require the application (and this library) to cross-check `request.shop` against a known/expected/installed shop list independent of the raw-body HMAC before trusting it, and document this requirement prominently since `Registry.process` currently implies HMAC validation alone is sufficient to trust the whole `WebhookMetadata` payload including `shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with attacker-controlled order data.
2. Shopify delivers `POST /webhooks` with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`, and the JSON body.
3. Attacker captures the raw body and HMAC, then sends a forged request directly to the same endpoint with `x-shopify-shop-domain: victim.myshopify.com` and the identical body/HMAC.
4. `HmacValidator.validate` recomputes HMAC over the (unchanged) raw body and it matches — validation passes: [6](#0-5) .
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled data>, ...)` [7](#0-6) , causing the host app to process attacker-controlled content as belonging to the victim tenant.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
