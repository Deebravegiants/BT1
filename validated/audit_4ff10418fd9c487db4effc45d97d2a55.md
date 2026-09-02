Confirmed: the `shop` field returned by `ShopifyAPI::Webhooks::Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [1](#0-0) , while `to_signable_string` (the value the HMAC is computed and verified over) is only the raw request body [2](#0-1) . `Registry.process` validates the HMAC using `HmacValidator.validate`, which calls `to_signable_string` and never touches `shop`, `topic`, `webhook_id`, or `api_version` [3](#0-2) [4](#0-3) . This is the exact "field acted on but not covered by the HMAC" identity-binding class named in the rules, so it is the strongest candidate here.

### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant webhook shop-spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC only over the raw request body, but the `shop` (and `topic`/`webhook_id`/`api_version`) values that the app's handler trusts and acts upon are taken straight from unauthenticated HTTP headers. An attacker who has previously observed one valid `(body, hmac)` pair for a topic they can trigger (e.g. by being a customer/collaborator on their own shop, or through any other means of obtaining a legitimately-signed webhook payload) can replay that exact body+hmac with a forged `shopify-shop-domain` header for a *different* shop, and `Registry.process` will accept it as valid and dispatch it to the handler labeled with the attacker-chosen shop.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the HMAC supplied by the request [5](#0-4) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [2](#0-1) ; the `shop` accessor is derived purely from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with no cryptographic binding to the signature at all [1](#0-0) .

`Registry.process` validates only `Utils::HmacValidator.validate(request)` and then immediately hands `request.shop` to the handler as the authoritative shop identity: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [3](#0-2) . Because the header is not part of the signed content, the equality the library implicitly claims to guarantee — "the shop this HMAC authenticates" == "the shop the handler receives" — does not hold. Any request whose *body* HMAC validates for the current `api_secret_key` will be accepted regardless of which shop's header is attached to it.

### Impact Explanation
This breaks a tenant-isolation boundary: a handler that uses `data.shop` (per `WebhookMetadata`) to decide which merchant's records to look up, redact, or mutate (e.g. `customers/redact`, `shop/redact`, `orders/*`) can be made to act on the wrong shop's data if any request carrying a validly-signed body for one topic can be re-submitted with a different shop header. Since this is the exact tenant-binding field the gem exposes as trusted output of webhook verification, exploitation yields cross-tenant data confusion in the app, which maps to a High/Critical-class impact (cross-tenant access) as defined by the scope rules.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimately HMAC-signed webhook body (for example, from a webhook fired for their own store, or any topic whose payload is not shop-specific/secret in content, such as `app/uninstalled` with an empty or generic body) and then replay it with a forged `shop-domain` header value at the target app's public webhook endpoint. No `api_secret_key`, access token, or privileged account is required — only observation of an unauthenticated request in transit or reuse of a webhook the attacker legitimately received for their own shop. This is a realistic, unprivileged-internet-user attack path, though it depends on the app's handler logic keying off `data.shop` without independent shop verification (e.g. checking that a session/token exists for that shop), which is the normal usage pattern documented for this gem's webhook handlers.

### Recommendation
Bind the shop domain (and ideally the webhook topic) into the signed content verified against the HMAC, or independently verify that `data.shop`/`request.shop` corresponds to a shop the app already has an active session/install record for before trusting it in handler logic. At minimum, document prominently that `Request#shop` is unauthenticated and must not be trusted for authorization decisions without cross-checking against a known installed shop.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook topic with a body that does not embed shop-identifying data in a way the handler checks (or simply body `"{}"`), capturing the resulting `(raw_body, x-shopify-hmac-sha256)` pair sent to the app's webhook endpoint.
2. Attacker replays the exact same HTTP request to the app's public webhook endpoint, but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only (unaffected by the header change) and succeeds [6](#0-5) .
4. The handler is invoked with `WebhookMetadata` whose `shop` is `"victim-shop.myshopify.com"`, even though the payload was never signed for, or sent by, that shop [7](#0-6) .

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
