### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
The webhook authenticity check performed by `Utils::HmacValidator.validate` only verifies the value returned by `VerifiableQuery#to_signable_string`. For incoming webhooks, `Webhooks::Request#to_signable_string` returns solely the raw HTTP body: [1](#0-0) 

Every other field that the gem trusts and hands to the application handler — `shop`, `topic`, `api_version`, `webhook_id` — is parsed directly from HTTP headers and is never included in the HMAC-signed material: [2](#0-1) 

`Webhooks::Registry.process` performs exactly one authenticity check — `Utils::HmacValidator.validate(request)` — and then immediately builds `WebhookMetadata` using `request.shop` taken straight from the (unsigned) header, handing it to the app's registered handler as the tenant identity for the event: [3](#0-2) 

`Utils::HmacValidator.validate_signature` confirms that the check is scoped only to `to_signable_string`, i.e., the body: [4](#0-3) 

The identity binding the code implicitly assumes is:
`HMAC-verified(raw_body) == authenticated(shop-domain header)`

but the actual binding enforced by the code is only:
`HMAC-verified(raw_body) == raw_body`

The `shop-domain` (and `topic`/`webhook-id`) header is never covered by the signature, so it can be swapped for any value while keeping a previously-obtained valid `(raw_body, hmac)` pair.

### Impact Explanation
Any unprivileged user who can install the app on their own store (i.e., a legitimate but unprivileged tenant) receives genuine webhook deliveries containing a body and a correctly computed `X-Shopify-Hmac-Sha256` value for their own shop. Because the header carrying the shop identity is outside the signed material, that same `(body, hmac)` pair remains "valid" according to `HmacValidator.validate` regardless of which `shop-domain` header accompanies it. An attacker can therefore submit a direct HTTP request to the application's public webhook endpoint, replaying their own valid `(body, hmac)` pair while substituting an arbitrary victim shop's domain in the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header. `Registry.process` will accept the request as authentic and dispatch it to the handler tagged with the attacker-chosen `shop`, causing the application to process/act on a webhook event attributed to a shop that never actually sent it — a cross-tenant identity confusion inside a Critical-severity category ("cross-tenant access").

### Likelihood Explanation
Likelihood is High for an app that has at least one merchant install (even the attacker's own trial/dev store): no access token, `client_secret`, or leaked credential is required — only a genuine webhook the attacker legitimately received for their own tenant, plus the ability to send an arbitrary HTTP POST to the app's public webhook route, which is by definition internet-reachable and unauthenticated (relying solely on `HmacValidator`).

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the signable material verified by `HmacValidator`, or otherwise cryptographically bind them to the body (e.g., verify the parsed body's own shop/tenant reference against the header, or require the host application to independently confirm the shop against a known, already-authenticated session/store record) before dispatching to the handler in `Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and a valid `X-Shopify-Hmac-Sha256` computed by Shopify over `B` with the app's `client_secret` (unknown to the attacker, but the resulting hmac is disclosed to them in the request they received).
2. Attacker crafts a new POST request directly to the app's public webhook endpoint using the same raw body `B` and the same `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` parses headers, exposing `shop` = `victim-shop.myshopify.com` while `to_signable_string` still returns `B` [5](#0-4) .
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `B` and compares to the supplied signature [6](#0-5) .
5. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though `victim-shop` never sent this webhook [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
