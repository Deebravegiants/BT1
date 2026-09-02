### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request **body**. All of the identity-carrying fields the host application actually consumes — `shop`, `topic`, `webhook_id`, and `api_version` — come from HTTP headers that are never included in the signed material. An attacker who can obtain one genuine, validly-signed webhook (e.g. by installing the app on their own store) can replay that same body/HMAC pair while substituting arbitrary values for the `shop-domain` (and other) headers, and the gem will treat the forged headers as authenticated.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, which are outside that signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) as authenticated tenant/routing identity, passing them straight into the handler: [3](#0-2) 

`HmacValidator.validate` only recomputes and compares the signature against `verifiable_query.to_signable_string`, i.e. the body — it never binds any header value into the signature: [4](#0-3) 

This is structurally the same class of bug as the reported `LBRouter.removeLiquidity` issue: a value that is *authenticated* (here, only the body) is not the same as the value that is *acted upon* (here, the header-derived `shop`/`topic`/`webhook_id`). The equality that should hold — `authenticated(shop) == used(shop)` — does not, because `shop` is never part of `authenticated(...)` at all.

### Impact Explanation
Because `shop` is not bound to the HMAC, any party who can obtain one legitimately-signed webhook body (trivial: install the app for free on a store they control, or capture any webhook delivery) can replay that exact `raw_body` + `hmac-sha256` header pair to the app's webhook endpoint while forging the `shop-domain` header to name a different, victim merchant. `HmacValidator.validate` will return `true` (the body and HMAC still match each other), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop. Any host application that uses `data.shop` to key per-tenant storage, look up a merchant's session/access token, or trigger merchant-specific side effects will process attacker-supplied data under the victim's tenant identity — a cross-tenant data-integrity/confidentiality break attributable to this gem's webhook verification design, not to host-app misuse of a documented contract.

### Likelihood Explanation
Exploitability requires only:
1. The ability to obtain any one valid `(raw_body, hmac-sha256)` pair for the app (trivially available to any developer/attacker who installs the app on a shop they control, since Shopify signs and delivers real webhooks to them).
2. The ability to POST to the app's public webhook endpoint with custom headers, which is standard for any internet-reachable webhook receiver.

No access to `api_secret_key`, access tokens, or any privileged credential is required — this is exploitable by any unprivileged internet user who can install a free trial/dev store and control what they send to the app's own webhook route.

### Recommendation
Bind the routing/tenant-identifying headers into the authenticated material, e.g. include `shop-domain`, `topic`, and `api-version` (and ideally the full raw header set relied upon) in the string that is HMAC-verified, or otherwise cryptographically bind them (for example, verify the reported `shop` against the shop the webhook subscription was registered for, or require a signed envelope covering headers+body) before trusting `request.shop`/`request.topic` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`. Shopify sends a real webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `HmacValidator.validate` computes the HMAC over `B` only and it matches `H`, so validation succeeds (see `lib/shopify_api/utils/hmac_validator.rb` lines 12-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38).
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed(B), ...)` (see `lib/shopify_api/webhooks/registry.rb` lines 188-199), and the host application acts on the attacker's data as if it originated from `victim.myshopify.com`.

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
