### Title
Webhook shop-domain header is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` identifier that is handed to the app's webhook handler comes from the `x-shopify-shop-domain` header, which is never included in the signed material. This breaks the identity binding `signed_body's_shop == request.shop`, allowing any unprivileged internet user who can obtain one validly-signed webhook payload (e.g., by installing the target app on their own free/dev store) to replay that payload against the app's webhook endpoint while substituting an arbitrary victim shop domain in the header, causing the app to process attacker-controlled data under another tenant's identity.

### Finding Description
The webhook `Request` object exposes `hmac` and `shop` as two independently-derived, unrelated values: [1](#0-0) 

- `hmac` is computed from the `hmac-sha256` header, decoded to raw bytes.
- `shop` is read verbatim from the `shop-domain` header, with no cryptographic relationship to the HMAC.

`to_signable_string` — the only material fed into the HMAC comparison — is the raw request body alone: [2](#0-1) 

`HmacValidator.validate` compares `verifiable_query.hmac` against an HMAC of `verifiable_query.to_signable_string` (the body) using the app's `api_secret_key`: [3](#0-2) 

`Registry.process` then dispatches to the handler using `request.shop`, which was never covered by that HMAC check: [4](#0-3) 

Because the HMAC is a function of the body and the app-wide `api_secret_key` only (not the shop domain), any raw body + HMAC pair that was legitimately signed by Shopify for **any** shop that has the app installed (including a shop the attacker created and controls, e.g. a free development store) will pass `HmacValidator.validate` regardless of which `shop-domain` header value is sent alongside it. The equality that should hold — "the shop whose Shopify instance produced/signed this body" == "the shop value the handler trusts as the tenant" — is not enforced anywhere in this gem's webhook-processing path.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker fully controls (a) the shop that produces a validly-signed body and (b) the header value asserting a different, victim shop identity, and the gem propagates the attacker-chosen `shop` value to the handler unauthenticated. If the app's webhook handler uses `WebhookMetadata#shop` to decide which tenant's data/session/API credentials to act on (the documented and intended use of this field), an attacker can cause the app to write attacker-controlled data (their own store's order/product/customer payload) into a victim shop's records, or trigger tenant-scoped side effects (e.g. sync, billing, notification) attributed to a shop they do not own. This satisfies the "cross-tenant access" criterion for a Critical/High-impact finding, since the gem's own verification logic — not host-application misuse — omits the shop domain from the authenticated payload.

### Likelihood Explanation
Likelihood is high for anyone motivated: no privileged credentials, TLS interception, or social engineering are required. The attacker only needs to (1) install the target Shopify app on a shop they control (trivial via a free Shopify Partners dev store) to receive genuinely Shopify-signed webhook deliveries, (2) capture the raw body and `x-shopify-hmac-sha256` value of one such webhook, and (3) replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to the victim's shop. All of the HMAC-validation logic in this gem will accept the forged request unchanged.

### Recommendation
Bind the shop domain into the authenticated material used for webhook verification, or otherwise cryptographically/contextually verify that the asserted `shop-domain` header corresponds to the shop that actually produced the signed body — for example, by including the shop domain in the signable string used by `Request#to_signable_string`/`HmacValidator`, or by requiring hosts to independently correlate `request.shop` against a known, previously-registered webhook endpoint/shop mapping before trusting it. At minimum, document prominently in this gem that `Webhooks::Request#shop` is unauthenticated and must not be trusted as a tenant identifier without additional verification by the host application.

### Proof of Concept
1. Attacker creates/uses a Shopify development store `attacker-shop.myshopify.com` and installs the target app, causing Shopify to deliver a real webhook (e.g. `orders/create`) to the app's webhook endpoint with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's `api_secret_key`.
2. Attacker captures the raw body `B` and header value `H = x-shopify-hmac-sha256`.
3. Attacker sends a new HTTP request to the same webhook endpoint with:
   - Body: `B` (unchanged)
   - `x-shopify-hmac-sha256`: `H` (unchanged, still valid because it only signs the body)
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.hmac` against `HMAC(body, api_secret_key)` — see [5](#0-4) .
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"`, even though the body content originated from the attacker's own shop — see [6](#0-5) .

### Citations

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
