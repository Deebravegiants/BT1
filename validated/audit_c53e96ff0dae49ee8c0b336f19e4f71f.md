### Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC verification exclusively to the raw request body, while `ShopifyAPI::Webhooks::Registry.process` trusts the unauthenticated `shop-domain` header to identify the tenant that the webhook belongs to. This breaks the intended identity binding `verified_bytes == acted_on_shop`, allowing any merchant who has installed the app on their own store (an unprivileged actor with respect to any other tenant) to replay a validly-HMAC'd webhook body while substituting an arbitrary `X-Shopify-Shop-Domain` header, causing the host application to process attacker-controlled data as if it originated from a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` computes the signable content used for HMAC validation solely from the raw body: [1](#0-0) 

The `shop` accessor, however, is read directly and unauthenticated from the `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `HmacValidator.validate`, and then forwards the unauthenticated `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute the digest only from `verifiable_query.to_signable_string`, i.e., only the body bytes for webhooks: [4](#0-3) 

Critically, the webhook HMAC secret (`Context.api_secret_key`) is the app's single, global client secret — shared across *every* shop that has installed the app — not a per-shop secret. This means any merchant who installs the app on their own shop legitimately receives, from real Shopify webhook deliveries, valid `(body, HMAC)` pairs signed with that same global secret. Because the `shop-domain` header is excluded from the signed content, that merchant can resend the same body/HMAC pair to the app's webhook endpoint while changing only the `shop-domain` header to point at a different (victim) shop. `Registry.process` will accept the request as authentic (`Invalid webhook HMAC.` is never raised) and dispatch `WebhookMetadata` claiming to be for the victim's shop.

The documentation reinforces that the gem's own verification is expected to fully vouch for the delivered metadata: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook," and the sample handler unconditionally trusts `data.shop` as the shop domain to act on. Nothing in the API surface signals to consuming apps that `data.shop` is unauthenticated relative to the payload.

This is the same defect class as the reference report: a field that is *acted on* (`shop`) is not covered by the same integrity check (`HMAC`) that is presented as having validated the whole message.

### Impact Explanation
An attacker with no privileged relationship to the victim shop — only the ability to install the target app on any shop they control — can forge webhook deliveries that the host application will process under a victim shop's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up/update the victim's session, inventory, orders, or trigger further authenticated API calls on the victim's behalf), this results in cross-tenant data injection/corruption, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that relies on this gem's webhook processing per its documented usage: an attacker only needs to install the app (a normal, unprivileged flow available to any developer/store owner) to obtain a valid `(body, HMAC)` pair, then can freely vary the `shop-domain` header when replaying the request to the app's public webhook endpoint. No access token, `client_secret`, or credential theft is required.

### Recommendation
Bind the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values into the value that is HMAC-verified, or otherwise cryptographically bind the shop to the signed payload (e.g., verify the header against a shop known to be authorized for the app/registration, or require callers to independently confirm the shop has a valid, previously-established session before trusting `WebhookMetadata#shop`). At minimum, update `Request#to_signable_string` so that verification covers the fields the gem later treats as trusted output, and document clearly that `shop` is not part of the HMAC unless changed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, becoming a legitimate (unprivileged) merchant of the app.
2. Attacker triggers a real webhook (e.g., `orders/create`) on their own store, capturing the exact raw body Shopify sends and the corresponding `X-Shopify-Hmac-Sha256` header value — both valid because they're signed with the app's shared `client_secret`.
3. Attacker sends a forged HTTP POST to the app's public webhook endpoint with the same raw body and HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only checks the HMAC against `@raw_body` [1](#0-0)  — validation succeeds.
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [5](#0-4)  and processes attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
