### Title
Webhook `shop` field is trusted from an unauthenticated header while only the raw body is covered by the HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The Aura Vault bug confuses two conceptually different values (vault shares vs. reward-pool shares) that should be bound together but aren't, causing the wrong entity to be trusted for a security-relevant operation. The corresponding pattern in this gem is `ShopifyAPI::Webhooks::Request`, where `Registry.process` verifies only the raw request body against the HMAC, while the `shop` (tenant identity) and `topic` fields used for dispatching and handed to application handlers are read directly from unauthenticated HTTP headers and are never part of the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (the body only) and compares it against `verifiable_query.hmac` (derived from the `hmac-sha256` header): [3](#0-2) [4](#0-3) 

After the HMAC check passes, `request.shop` (the unauthenticated header value) is forwarded verbatim into `WebhookMetadata`, which the host application's handler uses as the tenant identifier: [5](#0-4) 

The library's own documentation instructs developers to trust `data.shop` from the handler as "The shop domain of the webhook" without any caveat that it is unauthenticated: [6](#0-5) 

**Binding that is broken:** the equality that should hold is `shop_bound_by_hmac == shop_delivered_to_handler`. In this implementation, `shop_delivered_to_handler` is read from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is *not* part of `to_signable_string`, so `shop_bound_by_hmac` is effectively undefined — any shop value can be attached to a validly-signed body.

### Impact Explanation
Any party who has legitimately received one authentic, HMAC-signed webhook body (e.g., because they run their own shop with the same app installed, or because they've captured/replayed a previously-delivered webhook) can resend that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting an arbitrary value in the `shop-domain` header. Because `HmacValidator.validate` only checks the body against the secret, the tampered request still passes verification. The application-level handler then receives `WebhookMetadata` claiming the data originated from a different (victim) shop, causing the host app to attribute attacker-controlled webhook payloads to another tenant. This is a cross-tenant data/identity confusion: the app's downstream logic (order processing, product sync, billing state updates, etc., all keyed by `data.shop`) can be poisoned with data purportedly belonging to a shop the attacker doesn't control. This satisfies the "cross-tenant access" criterion for a Critical-impact finding without requiring possession of the app's `client_secret` or access token (the same signed body/HMAC pair the attacker already legitimately possesses is reused, only the routing header is altered).

### Likelihood Explanation
Exploitation requires only: (1) that the attacker be able to trigger delivery of at least one real webhook to themselves (e.g., install the app on a shop they control, or otherwise observe a legitimate webhook body+HMAC — for many popular topics with generic/near-empty bodies this is trivial, since the same body can validate for multiple different real HMACs across time if the payload content coincidentally repeats, and (2) that they can send an HTTP POST to the app's public webhook endpoint with custom headers, which is always possible since it's a plain HTTP endpoint with no additional origin/IP restriction. No access token, refresh token, or `client_secret` is needed, and no privileged account is required — this fits the "unprivileged internet user" threat model. Likelihood is tempered by the fact that this exact header/HMAC split mirrors Shopify's own documented webhook delivery format (Shopify itself does not sign the shop-domain header), so the design choice largely mirrors upstream protocol semantics; however, this library provides zero mitigating guidance or optional secondary binding (e.g., cross-checking the header shop against a shop associated with the given `webhook_id`/registration), unlike the sanitize/validate pattern the gem does apply elsewhere (see `Utils::ShopValidator.sanitize!` used in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`'s `migrate_to_expiring_token`).

### Recommendation
- Extend `to_signable_string` (or add a secondary integrity check within `Registry.process`) so that the `shop` (and ideally `topic`/`webhook_id`) header values are bound to the HMAC verification, rejecting requests where the header-derived tenant cannot be corroborated.
- At minimum, cross-validate the incoming `shop` header against the shop that owns the given `webhook_id`/topic registration (tracked server-side) before dispatching to the handler.
- Update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is derived from an HTTP header not covered by the Shopify webhook HMAC, and that applications must not treat it as an authenticated tenant identifier without additional verification.

### Proof of Concept
```ruby
# 1. Attacker legitimately receives (or replays) a real Shopify webhook for their own shop:
raw_body = '{"id":1,"note":"hello"}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
# (attacker cannot compute this themselves, but legitimately obtains it as a real recipient)

# 2. Attacker resends the exact same body+hmac to the target app's webhook endpoint,
#    but swaps the shop-domain header to the victim shop:
POST /callback/orders/create HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <real_hmac, base64>
X-Shopify-Shop-Domain: victim-shop.myshopify.com   # attacker-controlled, not signed
X-Shopify-Webhook-Id: <replayed-or-arbitrary>
X-Shopify-Api-Version: 2024-01

{"id":1,"note":"hello"}
```
```ruby
# Library-side verification:
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate only checks raw_body against real_hmac -> PASSES
# Handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# despite the payload actually belonging to the attacker's own shop.
```

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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```
