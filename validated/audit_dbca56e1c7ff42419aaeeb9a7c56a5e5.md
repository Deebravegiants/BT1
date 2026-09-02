## Analog Vulnerability Found

### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate(request)` succeeds, then immediately forwards `request.shop` (read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) to the app's handler as the tenant identifier. The HMAC that is actually verified only covers the raw request body — the shop-domain header is never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is read straight from a request header with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature only against `to_signable_string` (i.e., the raw body): [3](#0-2) 

`Registry.process` validates the HMAC, then constructs `WebhookMetadata` using `request.shop` and hands it to the registered handler as if it were verified data: [4](#0-3) 

The equality that should hold is: `shop-that-produced-the-HMAC-signed-payload == shop-value-delivered-to-the-handler`. Because the shop header sits entirely outside the signed bytes, an attacker can decouple these two values: take any webhook payload/HMAC pair that is valid for their own shop (an unprivileged internet user can install the app on their own dev/test store and legitimately receive real, HMAC-signed webhooks for it), then replay that exact `raw_body` + `hmac` to the app's webhook endpoint while substituting a different `shopify-shop-domain` header value. `HmacValidator.validate` still returns `true` because it only checks the body/secret pair, and `Registry.process` will dispatch to the handler with the attacker-chosen `shop`.

This is the same bug class as the Sherlock finding: verification is performed over one piece of data (auction values / raw body) while a materially different, unverified field (`previousOtcTolerance` / `shop`) is trusted and propagated downstream as authoritative.

### Impact Explanation
Any host application that relies on this gem's HMAC validation to trust `WebhookMetadata#shop` (as the docs and gem design imply — `HmacValidator.validate` is the single authenticity gate) can be tricked into attributing webhook data to the wrong tenant. Depending on the handler logic, this enables cross-tenant data confusion/access (e.g., writing order/customer data under another merchant's shop record, or triggering shop-scoped side effects for a shop the attacker doesn't control) — meeting the "cross-tenant access" Critical impact bar, since the shop binding that the handler depends on is not actually authenticated by this gem.

### Likelihood Explanation
Reachable by any unprivileged internet user who can install the target app on a shop they control (a standard, non-privileged action), capture one legitimately signed webhook, and replay it with a modified shop-domain header to the target app's webhook receiver endpoint. No access token, `client_secret`, or privileged credential is required — only the gem's own HMAC-validation logic (`Utils::HmacValidator.validate` + `Webhooks::Registry.process`) is at fault for not binding the shop identity into the signed payload/consumed value.

### Recommendation
Either (a) require host apps to independently verify the `shop` value returned in `WebhookMetadata` against their own session/shop store rather than treating it as authenticated by `HmacValidator.validate`, or (b) change `to_signable_string`/validation so the shop-domain header is included in the HMAC computation logic, or (c) explicitly document that `Utils::HmacValidator.validate` only authenticates the body and that `request.shop` must be treated as untrusted input by the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and legitimately triggers a webhook (e.g., `orders/create`), receiving a real request with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC(api_secret_key, B)`.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with the same body `B` and same `H`, but with header `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and matches `H` — validation passes.
4. `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` using the attacker-forged `"victim-shop.myshopify.com"` value and dispatches it to the handler as an authenticated event for the victim shop.

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
