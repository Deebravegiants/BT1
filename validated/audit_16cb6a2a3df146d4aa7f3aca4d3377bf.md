### Title
Webhook `shop-domain` (and topic/webhook-id) headers are trusted for tenant identification but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds the shop/tenant identity that is handed to application webhook handlers to the `x-shopify-shop-domain` HTTP header, while `ShopifyAPI::Utils::HmacValidator` only authenticates the raw request body. The header carrying the tenant identity is never part of the signed material, so a valid HMAC does not guarantee the `shop` value delivered to the handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic tie to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature only against `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, and then forwards the *unauthenticated* `request.shop` value straight to the application's handler as the tenant identifier: [4](#0-3) 

The binding that should hold is:
`shop value trusted by the HMAC == shop value delivered to the application handler`

In this implementation that equality does not hold — the HMAC only certifies `body`, not `(body, shop)`. Any actor who can obtain one legitimately-signed webhook body/HMAC pair for their own (attacker-controlled) shop — e.g., by installing the app on their own free development store and receiving a real webhook — can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value. `HmacValidator.validate` still succeeds because the body is unchanged, but `Registry.process` then invokes the handler with `WebhookMetadata.shop` set to the attacker-chosen value instead of the shop that actually produced the payload.

This is the exact bug class in the prompt: a field that is acted upon by the library/application (the tenant-identifying `shop`) but not covered by the HMAC that is supposed to authenticate the request.

### Impact Explanation
Applications built on this gem commonly key their persistence/session lookups and business logic off `WebhookMetadata#shop` (e.g., to find the merchant's session/access token, to route data updates, or to decide which tenant's records to mutate). Because the gem does not bind `shop` to the signature, an attacker who owns any shop where the target app is installed can forge webhook deliveries that impersonate a different, victim shop, causing the app to process attacker-supplied payload as though it belonged to that other tenant. That is a cross-tenant identity spoofing condition — the Critical-tier "cross-tenant access" impact category — that originates purely from this gem's request/HMAC design, not from any host-application misuse.

### Likelihood Explanation
Exploitation only requires the attacker to be a normal, unprivileged internet user who can install the target app on any shop they control (e.g., a free Shopify partner/development store) to receive one real, validly-signed webhook, and then send an HTTP POST directly to the app's public webhook endpoint with the same body/HMAC but a different `shop-domain` header. No access token, `client_secret`, TLS interception, or privileged account is required, and no dependency on the host app ignoring documented behavior — the gem's own `Registry.process`/`Request` code trusts the unauthenticated header by design.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the HMAC-signed material used for verification, or otherwise cryptographically bind the header-derived `shop` to the verified body before it is handed to `WebhookMetadata`/handlers. At minimum, `Registry.process` should cross-check `request.shop` against an independently-verified source (e.g., the shop associated with the currently active/expected session) rather than trusting the header outright once only the body HMAC has been validated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) so Shopify sends a legitimately signed request:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, body: `{...attacker-controlled order json...}`
2. Attacker captures this raw body and HMAC value.
3. Attacker sends a new HTTP POST directly to the app's public webhook endpoint, keeping the same body and `x-shopify-hmac-sha256` value, but changes the header to:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` (lines 26-31) succeeds because it only checks the body against the secret; it never inspects the `shop-domain` header.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-200) proceeds to call the app's handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop — spoofing cross-tenant identity with a cryptographically "valid" webhook.

### Citations

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
