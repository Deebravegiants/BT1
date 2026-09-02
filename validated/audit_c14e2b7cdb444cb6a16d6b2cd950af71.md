### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by verifying only the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to attribute the event to a tenant. Because the app's HMAC secret (`client_secret`) is shared across every shop that installs the app, any merchant who legitimately installs the app can capture a validly-signed webhook and replay it with a forged `shop-domain` header, causing the host app to process attacker-controlled webhook content under an arbitrary victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `shop` is read from a header that is never part of that signed content: [2](#0-1) 

`Registry.process` validates the HMAC of the request (i.e., of the body only) and, upon success, unconditionally forwards `request.shop` (the unauthenticated header value) to the handler: [3](#0-2) 

`HmacValidator.validate` only compares `verifiable_query.hmac` against a signature computed from `to_signable_string`, which for webhooks is the body alone: [4](#0-3) 

This breaks the identity binding that should hold: `shop domain used to attribute/route the webhook == shop domain cryptographically bound to the signed payload`. Instead, the equality that is actually enforced is only `HMAC(body, client_secret) == received_hmac`; the `shop-domain` header is disjoint from that check.

Because a single app's `client_secret` is shared across every shop that installs it (it is not a per-shop secret), any user who installs the app on their own store receives real, validly-signed webhooks. That attacker can capture the raw body + valid HMAC from a webhook addressed to their own shop, then replay the exact same body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (only the body is checked), so `Registry.process` calls the app's handler with `WebhookMetadata#shop` set to the victim's domain while the body content is fully attacker-controlled.

### Impact Explanation
This is a cross-tenant identity confusion: the gem allows an attacker to make the host application process attacker-chosen webhook payloads while attributing them to any shop domain the attacker chooses, without ever possessing that shop's credentials. Depending on how the host app's webhook handler uses `data.shop` (e.g., updating shop-scoped records, triggering shop-scoped side effects, or feeding into authorization decisions keyed by shop), this enables cross-tenant data injection/corruption — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires becoming a legitimate (even free/dev-store) installer of the target app to obtain one validly-HMAC-signed webhook body, then replaying it with a modified shop header — no access to the app's `client_secret`, access tokens, or any privileged account is needed, and no host-application misuse of a documented API is required since the gem itself never binds the shop header to the signature.

### Recommendation
Include the authenticated tenant identity in the value that is HMAC-verified, or otherwise reject/flag webhook `shop` values that were not part of the signed payload. Concretely:
- Extend `Request#to_signable_string` (or add a parallel check in `Registry.process`) to bind the `shop-domain` header value into what is authenticated, e.g. by requiring host apps to cross-check `request.shop` against a shop known to have this webhook registered/installed before trusting it, and document this requirement clearly.
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and that host apps must independently verify it corresponds to an installed shop before using it for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on their own (e.g., free development) store `attacker.myshopify.com`, and triggers a webhook (e.g., `orders/create`) that Shopify sends to the app's callback URL, signed with the app's shared `client_secret`.
2. Attacker intercepts/records the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (`H = HMAC-SHA256(client_secret, B)`).
3. Attacker replays a new POST request to the same webhook endpoint using body `B` and header `H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (a shop attacker does not control).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-derives the HMAC from `B` and compares to `H` — validation succeeds because `to_signable_string` never includes the shop header (`lib/shopify_api/webhooks/request.rb#L35-L38`).
5. The app's registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb#L198-L199`), causing the host app to process attacker-supplied webhook content as if it originated from `victim-shop.myshopify.com`.

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
