## Analysis

The report describes a broken identity binding: a field is *used* to make a security decision without being *covered* by the same authentication mechanism used to authorize the action. The closest reachable analog in this gem is the webhook signature verification path in `ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process`.

`Request#to_signable_string` returns only the raw HTTP body, and `Request#hmac` reads the `hmac-sha256` header — the HMAC is computed and verified purely over the body: [1](#0-0) [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from unauthenticated headers, and are never included in the signed payload: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then trusts `request.shop` and `request.topic` (header-derived, unsigned) to route and tag the event to a tenant: [4](#0-3) 

This is the exact bug class from the report: the binding "shop that authorized/signed this payload" == "shop the event is attributed to" is not enforced — `shop` is acted upon (used to construct `WebhookMetadata` and passed to the host app's handler) but not covered by the HMAC.

### Title
Webhook HMAC covers only the request body, not the `shop`/`topic` headers, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body alone, while `shop`, `topic`, `api_version`, and `webhook_id` are taken from HTTP headers that are not included in the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts these unauthenticated header values to attribute the event to a specific shop and route it to a handler.

### Finding Description
An attacker who has installed the target app on any shop they control receives a legitimately signed webhook (valid `raw_body` + `hmac` pair, computed with the app's shared `client_secret`). Because the HMAC only signs the body — `to_signable_string` returns `@raw_body` [2](#0-1)  — the attacker can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers with values belonging to a different (victim) shop. `HmacValidator.validate` will still succeed since the body is untouched [5](#0-4) , and `Registry.process` will dispatch the forged event, attributing attacker-supplied data to the victim's shop [4](#0-3) .

### Impact Explanation
This breaks the tenant isolation the webhook signature is meant to guarantee: `data.shop` passed into the host application's handler is not actually authenticated to the merchant it claims to represent. A host app that persists or acts on webhook data keyed by `data.shop` (e.g., updating that shop's records, marking uninstall/reinstall state, etc.) can be manipulated into applying attacker-controlled events to an arbitrary victim tenant — a cross-tenant access/injection vector, which matches the Critical impact bucket ("cross-tenant access").

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on a shop they control (an ordinary, unprivileged action any Shopify merchant/developer can take) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — no access to the app's `client_secret`, access tokens, or victim credentials is needed. This is a realistic, unprivileged-internet-user path.

### Recommendation
Bind the identity fields into the signed payload verification: derive `shop` from the verified body (many Shopify webhook payloads embed shop-identifying data) where possible, or require the host application/gem to cross-check the header-derived `shop`/`topic` against an out-of-band authenticated source (e.g., only accept `shop` values for shops with an active, previously-established session, and reject any topic/shop combination that wasn't the one actually registered for that specific installation). At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com`.
2. Attacker triggers/receives a legitimate webhook delivery, capturing `raw_body` and its valid `shopify-hmac-sha256` value (both computed with the app's shared secret).
3. Attacker POSTs the same `raw_body` to the app's webhook endpoint but rewrites headers:
 - `shopify-shop-domain: victim.myshopify.com`
 - `shopify-topic: <topic of attacker's choice, matching body>`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body's HMAC [5](#0-4)  — validation succeeds.
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [6](#0-5) , where `shop` is `victim.myshopify.com` despite the payload never having been signed for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
