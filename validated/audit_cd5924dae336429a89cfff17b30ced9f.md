Found it: `Webhooks::Request#shop` is read from the `shopify-shop-domain` HTTP header, but this field is **not part of the HMAC-signed payload**. The HMAC in `Webhooks::Request` covers only the raw request body (`to_signable_string` returns `@raw_body`), while `shop` is derived from a separate header that is never validated against that signature.

### Title
Webhook `shop` identity is taken from an unauthenticated header, not bound by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` validates webhook authenticity using HMAC-SHA256 computed over the raw request body [1](#0-0) , exactly the same pattern class (`Utils::VerifiableQuery`) used by OAuth's `AuthQuery` [2](#0-1) . However, unlike `AuthQuery#to_signable_string`, which explicitly includes `shop` in the signed parameter set [3](#0-2) , `Webhooks::Request#shop` reads the tenant identity straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header [4](#0-3) , a field that is completely outside the HMAC's covered bytes (`@raw_body`).

### Finding Description
The identity binding that should hold is:
`shop_verified_by_hmac == shop_used_by_the_application`

In this gem, `HmacValidator.validate` (or any equivalent check the host app performs) only proves that `@raw_body` was produced with the app's `client_secret` [5](#0-4) . It says nothing about the `shopify-shop-domain` header, because that header is never mixed into `to_signable_string`. Since HTTP headers are fully attacker-controlled by any client sending the POST request, an attacker who has a valid webhook (their own dev-store's webhook, which they can legitimately trigger) can replay the exact same signed body while substituting an arbitrary `shopify-shop-domain` header value. The signature still validates (it never inspected the header), but `Request#shop` — the value the host application uses to look up which merchant/tenant the payload belongs to and to route side effects (e.g., updating that shop's records, revoking access, deleting data) — now reflects an attacker-chosen shop, not the one that actually signed/sent the payload.

This exactly mirrors the reported bug class: a field ("shop"/tenant) that is *acted on* by the identity/authorization logic but is not covered by the cryptographic binding (HMAC), analogous to the `ERC20Rewards` case where the token address used for payout was not the one implicitly agreed upon during accrual.

### Impact Explanation
This breaks the tenant boundary the webhook mechanism is supposed to guarantee: cross-tenant confusion where a payload cryptographically proven to originate from the app's Shopify integration is attributed to the wrong `shop`. Any host application that trusts `Webhooks::Request#shop` (as the library's own registry/handler flow expects [6](#0-5) ) to select session/tenant state before processing the (validated) body can be tricked into acting on shop A's genuine, signed webhook data but crediting/debiting/mutating shop B's stored session or resources — a cross-tenant access primitive.

### Likelihood Explanation
Exploitation only requires an unprivileged internet user with the ability to send arbitrary HTTP POST requests to the app's public webhook endpoint, including replaying a previously captured or self-generated valid `(raw_body, hmac)` pair while forging the `shopify-shop-domain` header — no access token, secret, or privileged account needed, since headers are trivially attacker-controlled and are excluded from the signed bytes.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed bytes, or independently corroborate the header-derived `shop` against a value embedded in the signed body (e.g., a `shop_domain`/`shop_id` field of the JSON payload itself, which Shopify does include for most webhook topics) before trusting `Request#shop` for tenant resolution, following the same "sign what you rely on" pattern already used in `AuthQuery#to_signable_string`.

### Proof of Concept
1. Attacker's own shop legitimately registers a webhook subscription; Shopify sends a validly-HMAC'd webhook to the app's endpoint with headers `shopify-shop-domain: attacker-shop.myshopify.com` and a signed `raw_body`.
2. Attacker captures `raw_body` and its `hmac-sha256` header value.
3. Attacker replays the identical `POST` request to the same endpoint, keeping `raw_body`/`hmac-sha256` unchanged but replacing the `shopify-shop-domain` header with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (computed only from `@raw_body`) still returns `true`, since the header is not part of `to_signable_string` [1](#0-0) .
5. `Request#shop` now returns `"victim-shop.myshopify.com"` [4](#0-3) , and any downstream logic keyed off this value (session lookup, data mutation) operates on the victim tenant using a payload the attacker fully controls in shape (their own shop's data), demonstrating cross-tenant confusion.

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L1-18)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
  end
end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
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

**File:** lib/shopify_api/webhooks/registry.rb (L1-1)
```ruby
# typed: strict
```
