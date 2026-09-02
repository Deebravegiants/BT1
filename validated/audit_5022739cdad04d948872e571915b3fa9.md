### Title
Webhook `shop` domain is not covered by HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identity) is read from an unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` straight to the app's handler as the trusted tenant identifier, breaking the intended binding `HMAC-verified bytes == data the app trusts as this shop's data`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` (which in turn calls `to_signable_string`, i.e. only the body) and, once validated, immediately builds `WebhookMetadata` using the unauthenticated `request.shop` value and hands it to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` and `validate_signature` confirm the signature only ever covers `to_signable_string`: [4](#0-3) 

This is the exact bug class described in the report: a field (`shop`) is acted upon (used as the tenant key passed to the handler) but is not covered by the HMAC that is supposed to authenticate the request. The equality that should hold is:
`shop authenticated by Shopify's HMAC signature == shop the handler treats as the webhook's source`

Because the header is excluded from `to_signable_string`, this equality is not enforced. An attacker who operates their own Shopify store legitimately receives real webhooks (with a valid HMAC computed over the body using the app's `client_secret`) at the app's public webhook endpoint. Since the signature depends only on `@raw_body` and not on `shop`, the attacker can capture one of their own genuinely-signed webhook deliveries (valid HMAC, valid body) and replay it to the same endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still succeed (it only re-derives the signature from the untouched body), and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the victim's domain, together with attacker-controlled body content.

### Impact Explanation
This crosses a tenant boundary: it lets an unprivileged internet user (anyone able to sign up for a Shopify store) forge a webhook that the app's handler will process as originating from an arbitrary/victim shop, using data the attacker fully controls in `raw_body`. Depending on what the host application's handler does with `data.shop` and `data.body` (e.g., updating per-shop state, disabling features, writing to a shop-keyed database record, triggering uninstall/reinstall side effects), this is a cross-tenant data integrity/confusion vulnerability — the app cannot distinguish "real webhook about shop X" from "attacker's own webhook relabeled as shop X". This matches the Critical/High "cross-tenant access" impact category in scope.

### Likelihood Explanation
Likelihood is moderate-to-high: exploitation requires only an ordinary Shopify store (attacker-controlled, no special privileges) capable of receiving real webhooks for the target app, plus the ability to POST arbitrary HTTP requests to the app's public webhook callback endpoint (which is, by design, an unauthenticated public endpoint per `docs/usage/webhooks.md`). No access token, `client_secret`, or leaked credential is needed — only knowledge that the endpoint accepts standard Shopify webhook headers, which is documented behavior.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signable string used by `Request#to_signable_string`, or otherwise cryptographically bind the shop-domain header to the signed payload, so that `HmacValidator.validate` fails whenever the `shop` header has been tampered with independently of the body.

### Proof of Concept
1. Attacker registers/owns `attacker-shop.myshopify.com` and installs the target app, so the app registers webhooks with Shopify for that shop.
2. Shopify delivers a legitimate webhook to the app's callback endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body computed with app's client_secret>`
   - body: attacker-controlled JSON (attacker can influence some webhook payload content, e.g. product/order data on their own store).
3. Attacker intercepts/replays this exact request to the same endpoint but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`, leaving `raw_body` and `x-shopify-hmac-sha256` unchanged.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`@raw_body` only) — this matches, so validation passes at [5](#0-4) .
5. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"` and attacker-controlled body, even though Shopify never sent this webhook for the victim shop.

Note: I was unable to inspect `lib/shopify_api/webhooks/webhook_handler.rb`'s `WebhookMetadata` class definition directly (search only surfaced references, not its body) due to index limits; however, its usage at the two cited call sites is sufficient to establish that `request.shop` is passed through unverified as the trusted tenant identifier.

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
