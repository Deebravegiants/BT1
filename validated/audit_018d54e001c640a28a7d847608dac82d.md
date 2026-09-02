This confirms the finding: the docs explicitly instruct developers to call `ShopifyAPI::Webhooks::Registry.process` claiming "This will verify the request did indeed come from Shopify" — but the verification only covers the raw body bytes, and `data.shop` (used by the app to attribute the webhook and its side-effects to a specific merchant tenant) is taken directly from an unauthenticated header. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop-domain tenant attribution is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC of the raw request body against the app's shared `api_secret_key`. The `shop` value that identifies which merchant tenant the webhook belongs to — and that is handed to the app's handler for dispatch/attribution (`WebhookMetadata#shop`) — is read straight from the `x-shopify-shop-domain` header, which is never part of the HMAC-signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: ` [2](#0-1) `. `Utils::HmacValidator.validate` computes and compares the HMAC exclusively over this signable string using the app's `api_secret_key` (shared across every merchant that installs the app): ` [4](#0-3) `. Meanwhile `Request#shop` is pulled from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or the HMAC: ` [1](#0-0) `.

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: ` [3](#0-2) `. The library's own documentation tells developers that `process` "will verify the request did indeed come from Shopify" and shows the `data.shop` field being used directly for tenant attribution (e.g., `shop_domain: data.shop`) — implying the shop identity is trustworthy once `process` succeeds.

The identity binding that should hold is: `shop that produced a validly-HMAC'd body == shop attributed to that webhook by the handler`. Because the HMAC secret is shared across all shops that install a given app, and the signed material excludes the shop header, this equality does not hold: any body+HMAC pair that is valid for merchant A's webhook is equally "valid" (per this gem's check) when replayed with the `shop-domain` header rewritten to merchant B.

### Impact Explanation
An attacker who can install the target app on their own Shopify store (any unprivileged internet user can do this, e.g. via a free Shopify Partner development store) will receive genuine webhooks from Shopify for their own shop, each signed with the app's real `api_secret_key`/`client_secret`. Nothing in this gem requires the `api_secret_key` to be known by the attacker; the attacker only needs a legitimately-issued, validly-signed webhook of their own to work with. The attacker can then POST that exact `raw_body` (and its valid `x-shopify-hmac-sha256` value) directly to the app's public webhook endpoint, substituting the `x-shopify-shop-domain` header with a victim merchant's domain. `Registry.process` will accept this as authentic (HMAC check passes, since only the body is checked) and dispatch it to the app's handler with `data.shop` set to the victim's domain. If the handler uses `data.shop` to key stored data, trigger shop-scoped side effects, or select which merchant's session/access token to act on (a documented and expected usage pattern per `docs/usage/webhooks.md`), this results in cross-tenant confusion/spoofing — the attacker forges Shopify-originated events attributed to a shop they do not control, meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Likelihood is high for any multi-tenant app built on this gem following its documented pattern (single shared `api_secret_key`, single webhook endpoint dispatching by `data.shop`). The prerequisite — installing the app on an attacker-controlled shop to obtain a genuinely-signed webhook — is trivial and requires no privileged credentials, matching the "unprivileged internet user" threat model.

### Recommendation
Do not treat `request.shop` as authenticated merely because `Utils::HmacValidator.validate` succeeded. Either include the shop domain in the signed material used for verification, cross-check `request.shop` against an independently-trusted source (e.g., the shop already on record for the specific `webhook_id`/topic combination, or a per-shop webhook secret), or document explicitly and loudly that `shop`/`topic`/`webhook_id` headers are unauthenticated and must not be used for tenant attribution without additional verification.

### Proof of Concept
1. Install the target app (built with this gem) on an attacker-controlled development store `attacker.myshopify.com`.
2. Trigger a webhook subscribed by the app (e.g. `orders/create`) on that store; capture the raw POST body and its `x-shopify-hmac-sha256` header — both are validly signed with the app's real `api_secret_key`.
3. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which passes because only `@raw_body` is checked (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` and performs shop-scoped work believing it originated from the victim shop.

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
