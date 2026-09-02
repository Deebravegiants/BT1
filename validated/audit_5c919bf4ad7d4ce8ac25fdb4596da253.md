### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw body only, while the `shop` (and `topic`) values used to route and attribute the webhook to a tenant come from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`request.shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the HMAC, yet it is handed directly to the app's handler as the tenant identifier: [3](#0-2) [4](#0-3) 

`Utils::HmacValidator.validate` checks the HMAC using the single, app-wide `Context.api_secret_key` (the same secret for every shop that installs the app), not a per-shop secret: [5](#0-4) 

Because the signature is computed only over the body and the secret is shared across all installations, the equality the app relies on — "HMAC-verified bytes correspond to the `shop` field trusted by the handler" — does not hold. `shop` is a field acted on (used for tenant attribution/dispatch) but not covered by the HMAC. Any party who has legitimately installed the app on their own store receives genuine `(body, hmac)` pairs signed with that same shared secret. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop; the HMAC still validates because it never depended on the shop value, and the handler receives an attacker-crafted `WebhookMetadata` claiming to be the victim's shop.

The gem's own documentation confirms `data.shop` is intended to be trusted at face value by handlers ("The shop domain of the webhook"), with no guidance that it needs independent verification, so this is not a case of the host app misusing an undocumented API — it is the documented contract of `ShopifyAPI::Webhooks::Registry.process`.

### Impact Explanation
This breaks a tenant/identity boundary: an app installer with no special privileges can make the app process a webhook payload/body pair while cross-tenant-spoofing the `shop` attribute, causing the app to attribute (and possibly act on) a webhook body as belonging to a shop it did not originate from. This matches the "cross-tenant access" criterion for a High/Critical-impact analog, since the whole point of `process` is to authenticate the origin shop of the event before dispatching to shop-scoped handlers.

### Likelihood Explanation
Exploitability only requires the attacker to be a legitimate installer of the target app on their own store (an unprivileged, self-serve action available to any internet user who can install a Shopify app), capture one of their own genuine webhook deliveries (body + `x-shopify-hmac-sha256`), and resend it to the app's webhook endpoint with a substituted `shop-domain` header. No access to `api_secret_key` or any privileged credential is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed material verified by `HmacValidator`, or otherwise require handlers/callers to cross-check `request.shop` against a set of shops actually known/installed by the app before trusting the value, rather than passing the raw header value straight into `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged self-serve flow).
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` from their own webhook delivery (e.g., via their own logging endpoint, browser dev tools proxying their own traffic, etc. — no interception of anyone else's traffic needed).
4. Attacker resends `POST /callback/...` to the app's endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` and compares to `H` — it succeeds because both are unchanged. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to process the attacker's payload as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
