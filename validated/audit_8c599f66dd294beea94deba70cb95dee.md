### Title
Webhook shop-domain header is not covered by HMAC verification, allowing shop-identity spoofing in webhook processing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value taken from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header — a field that is never included in the HMAC-signed content. This breaks the identity binding: `shop used by the handler == shop authenticated by the HMAC`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `#shop` is read straight from an unauthenticated HTTP header: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac-sha256` header: [3](#0-2) 

Because `to_signable_string` is only the raw body, the shop-domain header is never part of the signed material. `Registry.process` then trusts `request.shop` as the tenant identity and forwards it, unverified, into the handler's data: [4](#0-3) 

An unprivileged internet user who controls any shop where the app is installed (a normal, self-service app install) can trigger a legitimate webhook delivery for their own shop, capture the `(raw_body, hmac-sha256)` pair from that delivery, and replay it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to an arbitrary victim shop domain. `HmacValidator.validate` will still succeed because the HMAC only covers `raw_body`, which is unchanged. The handler then receives `WebhookMetadata` claiming the body originated from the victim shop: [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" binding break: the equality that should hold — `WebhookMetadata#shop == shop that produced/authorized raw_body` — is not enforced anywhere in the gem.

### Impact Explanation
Any host application that relies on `WebhookMetadata#shop` (as returned by this gem's `Registry.process`) to select which merchant record, session, or access token to act on will process attacker-supplied content under a victim shop's identity. Depending on how a consuming app uses that shop value (e.g., to look up the target shop's session/access token and perform actions, or to route mandatory-webhook handling such as `shop/redact` or `app/uninstalled`), this enables cross-tenant confusion — an unprivileged actor causing app logic to be executed against a victim tenant's identity. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the ability to install the app on a shop the attacker controls (a standard, unprivileged action for any Shopify merchant/developer) and the ability to POST an HTTP request with a spoofed header to the app's public webhook endpoint. No knowledge of `api_secret_key` or any credential is required, since the attacker replays a byte-for-byte valid `(body, hmac)` pair they legitimately received.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise cryptographically tie the `shop-domain` header to the signed payload before trusting it (e.g., include the shop domain in the signable string, or independently verify the domain against a value obtained via an authenticated channel such as the session associated with the webhook subscription). At minimum, document that `WebhookMetadata#shop` is unauthenticated header data and must not be treated as a verified tenant identifier by consuming applications.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) to receive a genuine webhook POST with headers `x-shopify-hmac-sha256: H` and `x-shopify-shop-domain: attacker.myshopify.com`, and raw body `B`.
2. Replay a new HTTP POST to the app's webhook endpoint with the exact same raw body `B` and `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H`, so validation succeeds.
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled content is processed under the victim shop's identity.

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
